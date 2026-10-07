// Shared look for the paper's D3 figures. Runs in the browser page that lib/render.mjs builds.
// Units: every coordinate and font size is in points (1/72 in); the SVG viewBox is in points.
// Fonts: Latin Modern (the paper's body font) with optical sizes; Greek and math symbols fall back to
// Latin Modern Math. Colors follow the paper's TikZ tokens (paper.tex: fieldc, couplc, nullc, inkc).
(function () {
  const C = {
    ink: "#262626", ink2: "#595959", muted: "#8c8c8c", rule: "#bfbfbf", grid: "#ececec", paper: "#ffffff",
    field: "#E69F00", fieldSoft: "#fbe6bd", coupling: "#0072B2", couplingSoft: "#cfe3f0",
    up: "#CC3311", upSoft: "#f2c9bd", down: "#0072B2", downSoft: "#c7dcec",   // spins: red = talk, blue = not
    null: "#bdbdbd", nullBand: "#e9e9e9",
    green: "#009E73", pink: "#CC79A7", sky: "#56B4E9", vermillion: "#D55E00", yellow: "#F0E442",
  };
  const REG = { I: C.green, II: C.pink, III: C.coupling };
  const REG_SHAPE = { I: d3.symbolSquare, II: d3.symbolDiamond, III: d3.symbolCircle };
  const F = { body: "LM8, LMMath, serif", tick: "LM7, LMMath, serif", ital: "LM8i, LMMath, serif", bold: "LM8b, serif",
              sans: "LMSans8, sans-serif" };
  const SZ = { label: 7.6, tick: 6.6, small: 6.2, title: 7.8, panel: 8.2 };

  // ---- mini markup for labels: $x$ italic, _{..} subscript, ^{..} superscript (nesting not supported)
  function rich(sel, str, opt = {}) {
    const size = opt.size || SZ.label;
    sel.text(null);
    const toks = [];
    let i = 0, ital = false, buf = "";
    const flush = (extra = {}) => { if (buf) toks.push({ t: buf, ital, ...extra }); buf = ""; };
    while (i < str.length) {
      const ch = str[i];
      if (ch === "$") { flush(); ital = !ital; i++; continue; }
      if ((ch === "_" || ch === "^") && str[i + 1] === "{") {
        flush();
        const j = str.indexOf("}", i);
        toks.push({ t: str.slice(i + 2, j), ital, script: ch === "_" ? "sub" : "sup" });
        i = j + 1; continue;
      }
      buf += ch; i++;
    }
    flush();
    let shift = 0;
    for (const k of toks) {
      const ts = sel.append("tspan").text(k.t)
        .attr("font-family", k.ital ? F.ital : (opt.bold ? F.bold : F.body));
      if (k.script) {
        const d = k.script === "sub" ? size * 0.28 : -size * 0.38;
        ts.attr("font-size", size * 0.72).attr("dy", d - shift); shift = d;
      } else {
        ts.attr("font-size", size); if (shift) { ts.attr("dy", -shift); shift = 0; }
      }
    }
    return sel;
  }

  function text(g, x, y, str, o = {}) {
    const t = g.append("text").attr("x", x).attr("y", y)
      .attr("fill", o.fill || C.ink).attr("text-anchor", o.anchor || "start")
      .attr("dominant-baseline", o.baseline || "alphabetic");
    if (o.rotate) t.attr("transform", `rotate(${o.rotate},${x},${y})`);
    rich(t, str, { size: o.size || SZ.label, bold: o.bold });
    if (o.weight) t.attr("font-weight", o.weight);
    return t;
  }

  // ---- axes: thin rule, short outward ticks, 7-pt LM figures, optional light grid across the plot
  function axis(g, scale, side, o = {}) {
    const len = o.length;                            // plot extent perpendicular to the axis (for grid)
    const ticks = o.ticks || scale.ticks?.(o.n || 5) || scale.domain();
    const fmt = o.format || (scale.tickFormat ? scale.tickFormat(o.n || 5, o.spec) : (d) => d);
    const ax = g.append("g").attr("class", "axis");
    const horiz = side === "bottom" || side === "top";
    const [r0, r1] = scale.range();
    if (o.grid && len) {
      for (const t of ticks) {
        const p = scale(t) + (scale.bandwidth ? scale.bandwidth() / 2 : 0);
        ax.append("line").attr("stroke", C.grid).attr("stroke-width", 0.5)
          .attr(horiz ? "x1" : "y1", p).attr(horiz ? "x2" : "y2", p)
          .attr(horiz ? "y1" : "x1", 0).attr(horiz ? "y2" : "x2", side === "bottom" ? -len : side === "left" ? len : len);
      }
    }
    if (!o.noLine) ax.append("line").attr("stroke", C.ink2).attr("stroke-width", 0.5)
      .attr(horiz ? "x1" : "y1", Math.min(r0, r1)).attr(horiz ? "x2" : "y2", Math.max(r0, r1))
      .attr(horiz ? "y1" : "x1", 0).attr(horiz ? "y2" : "x2", 0);
    const tl = o.tickLen ?? 2.2, dir = side === "bottom" || side === "right" ? 1 : -1;
    for (const t of ticks) {
      const p = scale(t) + (scale.bandwidth ? scale.bandwidth() / 2 : 0);
      if (!o.noTicks) ax.append("line").attr("stroke", C.ink2).attr("stroke-width", 0.5)
        .attr(horiz ? "x1" : "y1", p).attr(horiz ? "x2" : "y2", p)
        .attr(horiz ? "y1" : "x1", 0).attr(horiz ? "y2" : "x2", dir * tl);
      const lab = fmt(t);
      if (lab === "" || lab == null) continue;
      const tt = ax.append("text").attr("fill", C.ink2).attr("font-family", F.tick).attr("font-size", o.size || SZ.tick);
      if (horiz) tt.attr("x", p).attr("y", dir * (tl + 1.6)).attr("text-anchor", o.anchor || "middle")
        .attr("dominant-baseline", side === "bottom" ? "hanging" : "alphabetic");
      else tt.attr("x", dir * (tl + 1.6)).attr("y", p).attr("text-anchor", side === "left" ? "end" : "start")
        .attr("dominant-baseline", "middle");
      if (o.rotateLabels) tt.attr("transform", `rotate(${o.rotateLabels},${+tt.attr("x")},${+tt.attr("y")})`)
        .attr("text-anchor", "end").attr("dominant-baseline", "middle");
      rich(tt, String(lab).replace(/^-(?=\d)/, "−"), { size: o.size || SZ.tick });
      tt.selectAll("tspan").attr("font-family", (d, i, n) => d3.select(n[i]).attr("font-family") === F.body ? F.tick : d3.select(n[i]).attr("font-family"));
    }
    if (o.title) {
      const off = o.titleOffset ?? (horiz ? 15 : 22);
      const mid = (r0 + r1) / 2;
      if (horiz) text(ax, mid, dir * off, o.title, { anchor: "middle", baseline: side === "bottom" ? "hanging" : "alphabetic", fill: C.ink });
      else text(ax, dir * off, mid, o.title, { anchor: "middle", rotate: -90, baseline: side === "left" ? "alphabetic" : "hanging", fill: C.ink });
    }
    return ax;
  }

  // panel tag: bold letter + short title, flush left at (x, y) = baseline
  function panel(g, x, y, letter, title, o = {}) {
    const t = g.append("text").attr("x", x).attr("y", y).attr("fill", C.ink);
    t.append("tspan").attr("font-family", F.bold).attr("font-size", SZ.panel).text(letter);
    if (title) {
      const s = t.append("tspan").attr("dx", 3.2);
      // reuse rich() by rendering into a temporary text, then moving tspans
      const tmp = g.append("text"); rich(tmp, title, { size: SZ.title });
      tmp.selectAll("tspan").each(function () { s.node().appendChild(this.cloneNode(true)); });
      tmp.remove();
      s.selectAll("tspan").attr("fill", o.fill || C.ink);
    }
    return t;
  }

  // direct label with a white halo, for labels drawn over data
  function halo(t, w = 2.2) {
    t.attr("paint-order", "stroke").attr("stroke", "#fff").attr("stroke-width", w).attr("stroke-linejoin", "round");
    return t;
  }

  function sym(type, size) { return d3.symbol().type(type).size(size)(); }

  // vertical CI bar + point (marker drawn with a 0.6-pt white ring so overlaps stay legible)
  function pointCI(g, x, y, lo, hi, o = {}) {
    const col = o.color || C.coupling;
    if (lo != null && hi != null) g.append("line").attr("x1", x).attr("x2", x).attr("y1", lo).attr("y2", hi)
      .attr("stroke", col).attr("stroke-width", o.ciw || 0.7).attr("stroke-linecap", "round").attr("opacity", o.ciOpacity ?? 1);
    g.append("path").attr("d", sym(o.shape || d3.symbolCircle, o.size || 9)).attr("transform", `translate(${x},${y})`)
      .attr("fill", o.fill ?? col).attr("stroke", o.stroke || "#fff").attr("stroke-width", o.sw ?? 0.6);
  }
  function pointCIh(g, x, y, lo, hi, o = {}) {
    const col = o.color || C.coupling;
    if (lo != null && hi != null) g.append("line").attr("y1", y).attr("y2", y).attr("x1", lo).attr("x2", hi)
      .attr("stroke", col).attr("stroke-width", o.ciw || 0.7).attr("stroke-linecap", "round").attr("opacity", o.ciOpacity ?? 1);
    g.append("path").attr("d", sym(o.shape || d3.symbolCircle, o.size || 9)).attr("transform", `translate(${x},${y})`)
      .attr("fill", o.fill ?? col).attr("stroke", o.stroke || "#fff").attr("stroke-width", o.sw ?? 0.6);
  }

  // small legend row: items [{label, color, shape|line|rect}], laid out left to right or as a column
  function legend(g, x, y, items, o = {}) {
    const lg = g.append("g").attr("transform", `translate(${x},${y})`);
    let cx = 0, cy = 0;
    for (const it of items) {
      const row = lg.append("g").attr("transform", `translate(${cx},${cy})`);
      if (it.rect) row.append("rect").attr("x", 0).attr("y", -3.6).attr("width", 7).attr("height", 5).attr("rx", 0.8)
        .attr("fill", it.color).attr("opacity", it.opacity ?? 1);
      else if (it.line) row.append("line").attr("x1", 0).attr("x2", 8).attr("y1", -1.2).attr("y2", -1.2)
        .attr("stroke", it.color).attr("stroke-width", it.width || 1.1).attr("stroke-dasharray", it.dash || null);
      else row.append("path").attr("d", sym(it.shape || d3.symbolCircle, it.size || 10)).attr("transform", "translate(3.5,-1.2)")
        .attr("fill", it.fill ?? it.color).attr("stroke", it.stroke || "#fff").attr("stroke-width", it.sw ?? 0.5);
      const t = text(row, it.line ? 11 : 9.5, 1.2, it.label, { size: o.size || SZ.small, fill: C.ink });
      const w = t.node().getComputedTextLength();
      if (o.column) cy += o.dy || 8.5; else cx += (it.line ? 11 : 9.5) + w + (o.gap || 7);
    }
    return lg;
  }

  const fmtMinus = (f) => (d) => f(d).replace("-", "−");

  window.S = { C, REG, REG_SHAPE, F, SZ, rich, text, axis, panel, halo, sym, pointCI, pointCIh, legend, fmtMinus,
    COL: 3.40, PAGE: 7.05 };
})();
