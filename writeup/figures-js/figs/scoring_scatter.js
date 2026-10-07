// Sec. III: credence p against value if true V for every scored claim; gray curves of equal EU = pV;
// colour = model family of the card's primary model; shape = mechanism depth; open = fragile; top 20 by EU labelled.
// Data: data/processed/paper-figs/scoring_scatter.json (export/scoring_scatter.py).
window.FIG = {
  width: 3.40, height: 3.35,
  draw(svg, D) {
    const { C, F } = S;
    const W = 3.40 * 72, H = 3.35 * 72;
    const g = svg.append("g");
    const M = { l: 27, r: 6, t: 5, b: 54 };
    const pw = W - M.l - M.r, ph = H - M.t - M.b;
    const gp = g.append("g").attr("transform", `translate(${M.l},${M.t})`);
    const x = d3.scaleLinear().domain([0, 4.0]).range([0, pw]);
    const y = d3.scaleLinear().domain([0.3, 1.0]).range([ph, 0]);
    const DEPTH = {
      M0: { shape: d3.symbolCircle, size: 13, label: "0: pattern" },
      M1: { shape: d3.symbolSquare, size: 11, label: "1: signature" },
      M2: { shape: d3.symbolDiamond, size: 17, label: "2: intervention" },
    };
    const FAM = [
      { key: "spins", label: "spins (M01, M02, M10)", color: "#0072B2" },
      { key: "fields", label: "fields (M11)", color: "#E69F00" },
      { key: "echoes", label: "echoes (M03, M09)", color: "#CC79A7" },
      { key: "relax", label: "relaxation (M16, M17)", color: "#56B4E9" },
      { key: "info", label: "info (M04, M15)", color: "#009E73" },
      { key: "other", label: "other", color: "#c4c4c4" },
    ];
    const famCol = Object.fromEntries(FAM.map((f) => [f.key, f.color]));

    // axes
    S.axis(gp.append("g").attr("transform", `translate(0,${ph})`), x, "bottom",
      { ticks: [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5], format: d3.format(".1f"), title: "value if true, $V$", titleOffset: 11 });
    S.axis(gp.append("g"), y, "left", { ticks: [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0], format: d3.format(".1f"),
      title: "credence $p$", titleOffset: 18 });

    // iso-EU curves, labelled where they leave the plot
    const clip = g.append("defs").append("clipPath").attr("id", "ssclip");
    clip.append("rect").attr("width", pw).attr("height", ph);
    const ge = gp.append("g").attr("clip-path", "url(#ssclip)");
    const euLabs = [], fixed = [];
    for (const eu of [0.5, 1, 1.5, 2, 2.5, 3]) {
      const pts = d3.range(eu / 1.0, 4.0 + 1e-9, 0.01).map((v) => [x(v), y(eu / v)]);
      ge.append("path").attr("d", d3.line()(pts)).attr("fill", "none").attr("stroke", "#d4d4d4").attr("stroke-width", 0.7);
      const vEnd = Math.min(4.0, eu / 0.3);
      euLabs.push({ eu, vEnd, pEnd: eu / vEnd });
    }
    for (const L of euLabs) {
      const atRight = L.vEnd >= 4.0 - 1e-9;
      const lab = `EU ${L.eu}`;
      const t = atRight ? S.text(gp, pw - 1, y(L.pEnd) - 2.0, lab, { anchor: "end", size: 5.9, fill: C.muted })
        : S.text(gp, x(L.vEnd) - 1.5, ph - 2.2, lab, { anchor: "end", size: 5.9, fill: C.muted });
      S.halo(t, 1.8);
      const bb = t.node().getBBox(); fixed.push({ x0: bb.x - 0.5, x1: bb.x + bb.width + 0.5, y0: bb.y, y1: bb.y + bb.height });
    }

    // credence cap
    gp.append("line").attr("x1", 0).attr("x2", pw).attr("y1", y(0.95)).attr("y2", y(0.95))
      .attr("stroke", C.null).attr("stroke-width", 0.6).attr("stroke-dasharray", "2.2,1.6");
    S.halo(S.text(gp, 3, y(0.95) - 2.0, "credence cap 0.95", { size: 5.9, fill: C.muted }), 1.8);

    // points: V is discrete, so dodge overlapping points sideways (deterministic swarm)
    const R = 2.35;
    const pts = D.rows.map((r) => ({ ...r, cx: x(r.V), cy: y(r.p) }))
      .sort((a, b) => d3.descending(a.eu, b.eu) || d3.ascending(a.id, b.id));
    const placed = [];
    for (const p of pts) {
      let best = 0;
      for (let k = 0; k < 40; k++) {
        const dx = (k % 2 ? 1 : -1) * Math.ceil(k / 2) * 0.9;
        const nx = x(p.V) + dx;
        if (placed.every((q) => Math.hypot(q.cx - nx, q.cy - p.cy) >= 2 * R - 0.2)) { best = dx; break; }
      }
      p.cx = x(p.V) + best; placed.push(p);
    }
    const gpt = gp.append("g");
    for (const p of [...pts].sort((a, b) => a.eu - b.eu)) {
      const st = DEPTH[p.m], col = famCol[p.family];
      gpt.append("path").attr("d", S.sym(st.shape, st.size)).attr("transform", `translate(${p.cx},${p.cy})`)
        .attr("fill", p.fragile ? "#fff" : col).attr("stroke", p.fragile ? col : "#fff")
        .attr("stroke-width", p.fragile ? 0.9 : 0.5);
    }

    // legend under the plot: colour = family (two rows), shape = depth, open = fragile
    const ly0 = M.t + ph + 26;
    S.text(g, 2, ly0, "model family", { size: 5.9, fill: C.ink2 });
    S.legend(g, 42, ly0, FAM.slice(0, 3).map((f) => ({ label: f.label, color: f.color, size: 12 })), { gap: 6, size: 5.9 });
    S.legend(g, 42, ly0 + 8, FAM.slice(3).map((f) => ({ label: f.label, color: f.color, size: 12 })), { gap: 6, size: 5.9 });
    S.text(g, 2, ly0 + 17, "mechanism depth", { size: 5.9, fill: C.ink2 });
    S.legend(g, 52, ly0 + 17, [...["M0", "M1", "M2"].map((k) => ({ label: DEPTH[k].label, shape: DEPTH[k].shape, size: DEPTH[k].size, color: C.ink2 })),
      { label: "open: fragile", shape: d3.symbolCircle, size: 13, color: C.ink2, fill: "#fff", stroke: C.ink2, sw: 0.8 }], { gap: 6, size: 5.9 });

    // labels for the top 20 by EU: pick, for each label, the free spot that costs least
    const fs = 5.9, lh = 4.4;
    const tmp = gp.append("text").attr("font-family", F.tick).attr("font-size", fs).text("H00");
    const lw = tmp.node().getComputedTextLength(); tmp.remove();
    const labs = pts.filter((p) => p.label);
    const obstacles = pts.map((p) => ({ x0: p.cx - R, x1: p.cx + R, y0: p.cy - R, y1: p.cy + R }));
    const capRect = { x0: 0, x1: 52, y0: y(0.95) - 7, y1: y(0.95) };
    const ov = (a, b) => Math.max(0, Math.min(a.x1, b.x1) - Math.max(a.x0, b.x0)) * Math.max(0, Math.min(a.y1, b.y1) - Math.max(a.y0, b.y0));
    // candidates: a direction and a clear gap between marker edge and label box (0.8 = touching, no leader;
    // >= 6 = with a leader long enough to read)
    const cand = [];
    for (const gap of [0.8, 6, 9, 13, 18, 24, 31]) for (let k = 0; k < 24; k++) {
      const a = (k / 24) * 2 * Math.PI; cand.push([Math.cos(a), Math.sin(a), gap]);
    }
    const box = (p, c) => {
      const [ux, uy, gap] = c, d = R + gap;
      // push the box out along (ux, uy) until its nearest point is d from the marker centre
      const hx = lw / 2, hy = lh / 2;
      let t = 0;
      for (let k = 0; k < 60; k++) {
        const bx = p.cx + ux * t, by = p.cy + uy * t;
        const dx = Math.max(Math.abs(bx - p.cx) - hx, 0), dy = Math.max(Math.abs(by - p.cy) - hy, 0);
        if (Math.hypot(dx, dy) >= d) break;
        t += 0.5;
      }
      const cx = p.cx + ux * t, cy = p.cy + uy * t;
      return { x0: cx - hx, x1: cx + hx, y0: cy - hy, y1: cy + hy, cx, cy, gap };
    };
    const segHits = (p, b, o) => {           // the drawn leader (marker -> nearest box point) crossing a box
      if (b.gap < 2) return 0;
      const qx = Math.max(b.x0, Math.min(p.cx, b.x1)), qy = Math.max(b.y0, Math.min(p.cy, b.y1));
      let h = 0;
      for (let i = 1; i <= 16; i++) {
        const t = i / 16, sx = p.cx + (qx - p.cx) * t, sy = p.cy + (qy - p.cy) * t;
        if (Math.hypot(sx - p.cx, sy - p.cy) < R + 0.5) continue;
        if (sx > o.x0 && sx < o.x1 && sy > o.y0 && sy < o.y1) h++;
      }
      return h;
    };
    const cost = (p, b, others) => {
      let c = 0;
      if (b.x0 < 1 || b.x1 > pw - 1 || b.y0 < 1 || b.y1 > ph - 1) c += 1e4;
      for (const o of obstacles) c += 40 * ov(b, o);
      for (const o of others) { c += 400 * ov(b, o); c += 30 * segHits(p, b, o); }
      c += 300 * ov(b, capRect);
      for (const o of fixed) c += 300 * ov(b, o);
      const dBox = (q) => Math.hypot(Math.max(b.x0 - q.cx, 0, q.cx - b.x1), Math.max(b.y0 - q.cy, 0, q.cy - b.y1));
      const own = dBox(p);
      for (const q of pts) if (q !== p) {            // a label must sit clearly nearer its own marker
        const dq = dBox(q);
        const need = b.gap < 2 ? own + 3.2 : 3.0;            // a leader names its marker
        if (dq < need) c += 60 * (need - dq);
        if (segHits(p, b, { x0: q.cx - R - 1.3, x1: q.cx + R + 1.3, y0: q.cy - R - 1.3, y1: q.cy + R + 1.3 })) c += 80;
      }
      c += 0.9 * b.gap + (b.gap > 1 ? 2 : 0);
      return c;
    };
    labs.forEach((p) => { p.box = box(p, cand[0]); });
    for (let pass = 0; pass < 20; pass++) {
      for (const p of labs) {
        const others = labs.filter((q) => q !== p).map((q) => q.box);
        let bestC = Infinity;
        for (const c of cand) { const b = box(p, c); const cc = cost(p, b, others); if (cc < bestC) { bestC = cc; p.box = b; } }
      }
    }
    const gl = gp.append("g");
    for (const p of labs) {
      const b = p.box, d = Math.hypot(b.cx - p.cx, b.cy - p.cy);
      const gap = Math.hypot(Math.max(b.x0 - p.cx, 0, p.cx - b.x1), Math.max(b.y0 - p.cy, 0, p.cy - b.y1));
      if (b.gap >= 5) {
        // leader from the marker edge to the nearest point of the label box
        const qx = Math.max(b.x0, Math.min(p.cx, b.x1)), qy = Math.max(b.y0 - 0.4, Math.min(p.cy, b.y1 + 0.4));
        const L = Math.hypot(qx - p.cx, qy - p.cy), s0 = (R + 0.5) / L, s1 = (L - 0.5) / L;
        gl.append("line").attr("x1", p.cx + (qx - p.cx) * s0).attr("y1", p.cy + (qy - p.cy) * s0)
          .attr("x2", p.cx + (qx - p.cx) * s1).attr("y2", p.cy + (qy - p.cy) * s1).attr("stroke", C.muted).attr("stroke-width", 0.4);
      }
      const t = gl.append("text").attr("x", b.x0).attr("y", b.y1 - 0.1).attr("font-family", F.tick).attr("font-size", fs)
        .attr("fill", C.ink2).text(p.id);
      S.halo(t, 1.6);
    }

  },
};
