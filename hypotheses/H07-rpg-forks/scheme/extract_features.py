"""H07 scheme, step 2: keyed content features per source blob (parse once per blob; snapshots join via fp_trees).

Run with:  uv run --with tree-sitter --with tree-sitter-javascript python hypotheses/H07-rpg-forks/scheme/extract_features.py

Blobs: every src/**/*.js blob that appears in the ancestor tree or in any post-T0 first-parent snapshot of any lineage
(fetched by id into the partial clones; see data/raw/repos/_source.md). Tests, docs and assets enter only the file-level
feature (path -> blob) in fp_trees.parquet.

Features (all keyed within a file; the snapshot key prepends the path):
  numbers    ctx = code path of the literal: declarator / class / function / method names, object keys, array
             elements (labelled [id=..] or [name=..] when the element object has such a property, else [i]),
             assignment targets ('this.hp='), callees ('Math.max()'); k = occurrence index within (ctx);
             value = float; data = True when the literal sits directly in an object pair, array, or declarator
             (a parameter, not an operand in logic code).
  functions  qualname (Class.method, name, obj.key) with occurrence index; value = 64-bit hash of the body text
             with whitespace collapsed.
  idents     declared names: function, class, method, variable declarator identifiers (set-valued feature).
  names      string values of name / title / displayName / label properties (content names; ctx-keyed and set).
  entities   objects carrying both an id-like (id / key) and a name-like property: entity id -> name.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import polars as pl
import tree_sitter as ts
import tree_sitter_javascript as tsjs

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import UTC, git_commit  # noqa: E402

REPOS = ROOT / "data/raw/repos"
OUT = ROOT / "data/processed/H07-rpg-forks"
REPO = {"ancestor": "rpg-game", "origin": "rpg-game", "best": "rpg-game-best", "rest": "rpg-game-rest",
        "restweek": "rpg-game-rest-week"}
NAME_KEYS = {"name", "title", "displayName", "label"}
ID_KEYS = {"id", "key"}
LANG = ts.Language(tsjs.language())
PARSER = ts.Parser(LANG)


def h64(b: bytes) -> int:
    return int.from_bytes(hashlib.blake2b(b, digest_size=8).digest(), "big", signed=True)


def txt(n) -> str:
    return n.text.decode("utf8", "replace")


def key_text(k) -> str:
    if k.type == "string":
        return txt(k)[1:-1]
    return txt(k)


def str_value(n):
    if n is not None and n.type == "string":
        return txt(n)[1:-1]
    if n is not None and n.type == "template_string" and n.named_child_count == 0:
        return txt(n)[1:-1]
    return None


def obj_label(obj):
    """[id=..] / [name=..] label of an object literal used as an array element."""
    if obj.type != "object":
        return None
    for p in obj.named_children:
        if p.type == "pair":
            k = key_text(p.child_by_field_name("key"))
            if k in ("id", "key", "name", "type"):
                v = str_value(p.child_by_field_name("value"))
                if v is not None:
                    return f"[{k}={v[:40]}]"
    return None


def ctx_of(node):
    """Code path of a node: list of segments from the root."""
    segs = []
    child = node
    n = node.parent
    while n is not None:
        t = n.type
        if t == "pair":
            segs.append(key_text(n.child_by_field_name("key"))[:40])
        elif t == "variable_declarator":
            nm = n.child_by_field_name("name")
            segs.append(txt(nm)[:40] if nm is not None else "?")
        elif t in ("function_declaration", "class_declaration", "method_definition", "generator_function_declaration"):
            nm = n.child_by_field_name("name")
            segs.append(txt(nm)[:40] if nm is not None else "?")
        elif t == "array":
            lab = obj_label(child)
            if lab is None:
                idx = [c.id for c in n.named_children].index(child.id) if child.id in [c.id for c in n.named_children] else -1
                lab = f"[{idx}]"
            segs.append(lab)
        elif t == "assignment_expression":
            left = n.child_by_field_name("left")
            if left is not None and left.id != child.id:
                segs.append(txt(left)[:40] + "=")
        elif t == "call_expression":
            fn = n.child_by_field_name("function")
            if fn is not None and fn.id != child.id:
                segs.append(txt(fn)[:40] + "()")
        child = n
        n = n.parent
    return "/".join(reversed(segs))


def qualname(n):
    t = n.type
    if t in ("function_declaration", "generator_function_declaration", "class_declaration"):
        nm = n.child_by_field_name("name")
        return txt(nm) if nm is not None else None
    if t == "method_definition":
        nm = n.child_by_field_name("name")
        cls = n.parent.parent if n.parent is not None else None
        cname = txt(cls.child_by_field_name("name")) if cls is not None and cls.type in ("class_declaration", "class") \
            and cls.child_by_field_name("name") is not None else "?"
        return f"{cname}.{txt(nm)}" if nm is not None else None
    if t in ("arrow_function", "function_expression", "function"):
        p = n.parent
        if p is not None and p.type == "variable_declarator":
            return txt(p.child_by_field_name("name"))
        if p is not None and p.type == "pair":
            return ctx_of(p) + "/" + key_text(p.child_by_field_name("key"))
    return None


def extract(blob: str, data: bytes):
    tree = PARSER.parse(data)
    nums, funcs, idents, names, ents = [], [], [], [], []
    occ_n, occ_f, occ_s = {}, {}, {}
    stack = [tree.root_node]
    while stack:
        n = stack.pop()
        t = n.type
        if t == "number":
            par = n.parent
            raw = txt(n)
            node_for_ctx = n
            if par is not None and par.type == "unary_expression" and txt(par).startswith("-"):
                raw = "-" + raw
                node_for_ctx = par
                par = par.parent
            try:
                val = float(raw.replace("_", "")) if not raw.lower().startswith(("0x", "-0x", "0b", "0o")) \
                    else float(int(raw.replace("-", ""), 0)) * (-1 if raw.startswith("-") else 1)
            except ValueError:
                val = None
            ctx = ctx_of(node_for_ctx)
            k = occ_n.get(ctx, 0); occ_n[ctx] = k + 1
            is_data = par is not None and par.type in ("pair", "array", "variable_declarator")
            nums.append((blob, ctx, k, val, raw[:30], is_data))
        elif t in ("function_declaration", "generator_function_declaration", "method_definition", "arrow_function",
                   "function_expression", "function"):
            q = qualname(n)
            if q:
                body = n.child_by_field_name("body")
                if body is not None:
                    k = occ_f.get(q, 0); occ_f[q] = k + 1
                    funcs.append((blob, q[:120], k, h64(re.sub(rb"\s+", b" ", body.text))))
                if t != "method_definition":
                    pass
            if t in ("function_declaration", "generator_function_declaration"):
                idents.append((blob, txt(n.child_by_field_name("name")), "function"))
            elif t == "method_definition" and n.child_by_field_name("name") is not None:
                idents.append((blob, txt(n.child_by_field_name("name")), "method"))
        elif t == "class_declaration" and n.child_by_field_name("name") is not None:
            idents.append((blob, txt(n.child_by_field_name("name")), "class"))
        elif t == "variable_declarator":
            nm = n.child_by_field_name("name")
            if nm is not None and nm.type == "identifier":
                idents.append((blob, txt(nm), "var"))
        elif t == "pair":
            k = key_text(n.child_by_field_name("key"))
            if k in NAME_KEYS:
                v = str_value(n.child_by_field_name("value"))
                if v:
                    ctx = ctx_of(n.parent) if n.parent is not None else ""
                    j = occ_s.get((ctx, k), 0); occ_s[(ctx, k)] = j + 1
                    names.append((blob, ctx[:200], k, j, v[:120]))
        elif t == "object":
            idv = nmv = None
            for p in n.named_children:
                if p.type == "pair":
                    k = key_text(p.child_by_field_name("key"))
                    if k in ID_KEYS and idv is None:
                        idv = str_value(p.child_by_field_name("value"))
                    elif k == "name" and nmv is None:
                        nmv = str_value(p.child_by_field_name("value"))
            if idv and nmv:
                ents.append((blob, idv[:80], nmv[:120]))
        stack.extend(reversed(n.children))
    return nums, funcs, idents, names, ents, tree.root_node.has_error


def main():
    trees = pl.read_parquet(OUT / "fp_trees.parquet").filter(pl.col("path").str.contains(r"^src/.*\.js$"))
    pairs = trees.with_columns(pl.col("lineage").replace_strict(REPO).alias("repo")).select("repo", "blob").unique()
    N, F, I, S, E, err = [], [], [], [], [], []
    for repo, g in pairs.group_by("repo"):
        blobs = g["blob"].to_list()
        p = subprocess.run(["git", "-C", str(REPOS / f"{repo[0]}.git"), "cat-file", "--batch"],
                           input=("\n".join(blobs) + "\n").encode(), capture_output=True, check=True)
        buf, pos = p.stdout, 0
        for b in blobs:
            hdr_end = buf.index(b"\n", pos)
            sha, typ, size = buf[pos:hdr_end].split()
            size = int(size)
            data = buf[hdr_end + 1: hdr_end + 1 + size]
            pos = hdr_end + 1 + size + 1
            assert sha.decode() == b and typ == b"blob"
            n_, f_, i_, s_, e_, has_err = extract(b, data)
            N += n_; F += f_; I += i_; S += s_; E += e_
            err.append((b, has_err, size))
    pl.DataFrame(N, schema=["blob", "ctx", "k", "value", "raw", "data"], orient="row").unique(
        subset=["blob", "ctx", "k"]).write_parquet(OUT / "blob_numbers.parquet")
    pl.DataFrame(F, schema=["blob", "qualname", "k", "body_hash"], orient="row").unique(
        subset=["blob", "qualname", "k"]).write_parquet(OUT / "blob_functions.parquet")
    pl.DataFrame(I, schema=["blob", "ident", "kind"], orient="row").unique().write_parquet(OUT / "blob_idents.parquet")
    pl.DataFrame(S, schema=["blob", "ctx", "field", "k", "value"], orient="row").unique(
        subset=["blob", "ctx", "field", "k"]).write_parquet(OUT / "blob_names.parquet")
    pl.DataFrame(E, schema=["blob", "entity_id", "name"], orient="row").unique().write_parquet(
        OUT / "blob_entities.parquet")
    pl.DataFrame(err, schema=["blob", "parse_error", "size"], orient="row").unique().write_parquet(
        OUT / "blob_meta.parquet")
    p = OUT / "_provenance.json"
    prov = json.loads(p.read_text()) if p.exists() else {}
    prov["extract_features"] = {"built_by": "hypotheses/H07-rpg-forks/scheme/extract_features.py",
                                "git_commit": git_commit(), "inputs": ["fp_trees.parquet", "data/raw/repos/*.git blobs"],
                                "params": {"parser": "tree-sitter-javascript", "files": "src/**/*.js"},
                                "built_at": dt.datetime.now(UTC).isoformat()}
    p.write_text(json.dumps(prov, indent=1))
    print(f"blobs {len(err)}, parse errors {sum(e[1] for e in err)}, numbers {len(N)}, functions {len(F)}, "
          f"idents {len(I)}, names {len(S)}, entities {len(E)}")


if __name__ == "__main__":
    main()
