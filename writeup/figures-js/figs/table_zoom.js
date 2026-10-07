// Sec. III: (a) part of the hypothesis x physics-model table (glyph = role of the model, color = outcome);
// (b) one cell, H08 under model 02, resolved into verdicts per goal period and per natural experiment.
// Data: data/processed/paper-figs/table_zoom.json (export/table_zoom.py).
window.FIG = {
  width: 7.05, height: 2.78,
  draw(svg, D) {
    const { C, F } = S;
    const W = 7.05 * 72, H = 2.78 * 72;
    const g = svg.append("g");
    const defs = svg.append("defs");

    // red-gray-green outcome scale (house rule), light gray = untested
    const OUT = { supported: S.C.green, mixed: "#9a9a9a", refuted: S.C.up, failed: S.C.up, untested: "#d6d6d6",
      "n/a": "#d6d6d6" };
    const ROLE = {
      primary: { shape: d3.symbolCircle, size: 36, open: false, label: "primary" },
      secondary: { shape: d3.symbolCircle, size: 11, open: false, label: "secondary" },
      rival: { shape: d3.symbolDiamond, size: 19, open: false, label: "rival" },
      null: { shape: d3.symbolSquare, size: 13, open: true, label: "null" },
      tool: { shape: d3.symbolTriangle, size: 14, open: true, label: "tool" },
    };
    const res = defs.append("pattern").attr("id", "reserved").attr("patternUnits", "userSpaceOnUse")
      .attr("width", 2.4).attr("height", 2.4).attr("patternTransform", "rotate(45)");
    res.append("rect").attr("width", 2.4).attr("height", 2.4).attr("fill", "#f4f4f4");
    res.append("rect").attr("width", 0.8).attr("height", 2.4).attr("fill", "#cfcfcf");

    // ------------------------------------------------------------------ (a) the table
    S.panel(g, 0, 8, "a", "Hypothesis × physics model (H01–H20)");
    const A = { x: 22, y: 50, cw: 12.4, rh: 6.9 };
    const B = { x: 286, y: 36, tw: 11.0, th: 12.6, gap: 1.25, rowPitch: 26.5 };
    const cols = D.cols, rows = D.rows;
    const cx = (m) => A.x + (cols.indexOf(m) + 0.5) * A.cw, cy = (h) => A.y + (rows.indexOf(h) + 0.5) * A.rh;
    const ga = g.append("g");
    for (const m of cols) ga.append("line").attr("x1", cx(m)).attr("x2", cx(m)).attr("y1", A.y).attr("y2", A.y + rows.length * A.rh)
      .attr("stroke", C.grid).attr("stroke-width", 0.5);
    for (const h of rows) ga.append("line").attr("x1", A.x).attr("x2", A.x + cols.length * A.cw).attr("y1", cy(h)).attr("y2", cy(h))
      .attr("stroke", C.grid).attr("stroke-width", 0.5);
    // column heads: model number + short name, slanted
    cols.forEach((m, i) => {
      const x0 = cx(m) - 1, y0 = A.y - 3;
      const t = g.append("text").attr("x", x0).attr("y", y0).attr("transform", `rotate(-55,${x0},${y0})`)
        .attr("font-size", 5.9).attr("fill", m === D.zoom.model ? C.ink : C.ink2);
      t.append("tspan").attr("font-family", m === D.zoom.model ? F.bold : F.tick).text(m + " ");
      t.append("tspan").attr("font-family", F.body).text(D.short[i]);
    });
    for (const h of rows) {
      const t = S.text(g, A.x - 3, cy(h) + 2.0, h, { anchor: "end", size: 5.9, fill: h === D.zoom.h ? C.ink : C.ink2 });
      t.selectAll("tspan").attr("font-family", h === D.zoom.h ? F.bold : F.tick);
    }
    const zx = cx(D.zoom.model), zy = cy(D.zoom.h);
    // pointer from the cell to (b): along the H08 row (under the glyphs), then up to the tiles
    defs.append("marker").attr("id", "tzarrow").attr("viewBox", "0 0 6 6").attr("refX", 5.4).attr("refY", 3)
      .attr("markerWidth", 4.4).attr("markerHeight", 4.4).attr("orient", "auto")
      .append("path").attr("d", "M0,0.4L6,3L0,5.6z").attr("fill", C.ink);
    {
      const xe = A.x + cols.length * A.cw + 4, x1 = B.x - 4, y1 = B.y + B.th / 2;
      const path = `M${zx + A.cw / 2},${zy}H${xe} C${xe + 26},${zy} ${x1 - 30},${y1} ${x1},${y1}`;
      ga.append("path").attr("d", path).attr("fill", "none").attr("stroke", C.ink2).attr("stroke-width", 0.55)
        .attr("marker-end", "url(#tzarrow)");
    }
    // glyphs: primaries last so they sit on top
    const order = { tool: 0, null: 1, secondary: 2, rival: 3, primary: 4 };
    for (const c of [...D.cells].sort((a, b) => order[a.role] - order[b.role])) {
      const R = ROLE[c.role] || ROLE.secondary, col = OUT[c.outcome] || OUT.untested;
      ga.append("path").attr("d", S.sym(R.shape, R.size)).attr("transform", `translate(${cx(c.model)},${cy(c.h) + (c.role === "tool" ? 0.4 : 0)})`)
        .attr("fill", R.open ? "#fff" : col).attr("stroke", R.open ? col : "#fff").attr("stroke-width", R.open ? 0.8 : 0.5);
    }
    // the zoomed cell
    ga.append("rect").attr("x", zx - A.cw / 2 + 0.3).attr("y", zy - A.rh / 2 + 0.1).attr("width", A.cw - 0.6).attr("height", A.rh - 0.2)
      .attr("fill", "none").attr("stroke", C.ink).attr("stroke-width", 0.9);

    // ------------------------------------------------------------------ (b) one cell, per goal period
    S.panel(g, B.x - 8, 8, "b", `One cell: ${D.zoom.h} under model ${D.zoom.model} (${D.name[D.zoom.model]})`);
    S.text(g, B.x - 8 + 7.4, 17.5, `${D.zoom.h}: ${D.zoom.title}. Verdict in each goal period`, { size: 6.2, fill: C.ink2 });
    const ncol = 17;
    const tile = (k) => ({ x: B.x + (k % ncol) * (B.tw + B.gap), y: B.y + Math.floor(k / ncol) * B.rowPitch });
    const gb = g.append("g");
    D.zoom.periods.forEach((p, k) => {
      const T = tile(k);
      const fill = p.verdict ? OUT[p.verdict] : (p.reserved ? "url(#reserved)" : OUT.untested);
      gb.append("rect").attr("x", T.x).attr("y", T.y).attr("width", B.tw).attr("height", B.th).attr("rx", 0.8).attr("fill", fill);
      const t = S.text(gb, T.x + B.tw / 2, T.y + B.th / 2 + 2.0, String(p.goal), { anchor: "middle", size: 5.9,
        fill: p.verdict ? "#fff" : (p.reserved ? C.muted : C.ink2) });
      t.selectAll("tspan").attr("font-family", F.tick);
    });
    // regime brackets under each tile row
    for (let r = 0; r < 3; r++) {
      const ks = d3.range(r * ncol, Math.min(51, (r + 1) * ncol));
      const segs = d3.groups(ks, (k) => D.zoom.periods[k].regime);
      for (const [reg, kk] of segs) {
        const a = tile(kk[0]).x + 0.4, b = tile(kk[kk.length - 1]).x + B.tw - 0.4, yb = tile(kk[0]).y + B.th + 3.2;
        gb.append("path").attr("d", `M${a},${yb - 1.8}V${yb}H${b}V${yb - 1.8}`).attr("fill", "none")
          .attr("stroke", C.ink2).attr("stroke-width", 0.45);
        const lab = (b - a) > 40 ? `regime ${reg}` : reg;
        const t = S.text(gb, (a + b) / 2, yb + 0.2, lab, { anchor: "middle", size: 5.8, fill: C.ink2, baseline: "middle" });
        const w = t.node().getComputedTextLength();
        gb.insert("rect", () => t.node()).attr("x", (a + b) / 2 - w / 2 - 1.4).attr("y", yb - 2.6).attr("width", w + 2.8)
          .attr("height", 5.2).attr("fill", "#fff");
      }
    }
    // natural experiments
    const ny = B.y + 3 * B.rowPitch + 8;
    S.text(gb, B.x, ny + (B.th - 1) / 2 + 2.0, "across natural experiments", { size: 6.2, fill: C.ink2 });
    D.zoom.nes.forEach((n, i) => {
      const x0 = B.x + 90 + i * 31;
      const desc = n.verdict === "descriptive";
      gb.append("rect").attr("x", x0).attr("y", ny).attr("width", 28).attr("height", B.th - 1).attr("rx", 0.8)
        .attr("fill", desc ? "#fff" : (OUT[n.verdict] || "#e4e4e4")).attr("stroke", desc ? C.muted : null).attr("stroke-width", 0.6);
      const t = S.text(gb, x0 + 14, ny + (B.th - 1) / 2 + 2.0, n.id, { anchor: "middle", size: 5.9, fill: desc ? C.ink2 : "#fff" });
      t.selectAll("tspan").attr("font-family", F.tick);
    });

    // ------------------------------------------------------------------ shared key (bottom right)
    const kg = g.append("g").attr("transform", `translate(${B.x},${H - 30})`);
    const rowKey = (yy, title, items) => {
      S.text(kg, 0, yy, title, { size: 6.2, fill: C.ink2 });
      let xx = 44;
      for (const it of items) {
        it.draw(xx, yy);
        const t = S.text(kg, xx + 9, yy, it.label, { size: 6.2, fill: C.ink });
        xx += 9 + t.node().getComputedTextLength() + 8;
      }
    };
    const glyph = (k) => ({ label: ROLE[k].label, draw: (xx, yy) => kg.append("path").attr("d", S.sym(ROLE[k].shape, ROLE[k].size))
      .attr("transform", `translate(${xx + 3.2},${yy - 2})`).attr("fill", ROLE[k].open ? "#fff" : C.ink2)
      .attr("stroke", ROLE[k].open ? C.ink2 : "#fff").attr("stroke-width", ROLE[k].open ? 0.8 : 0.5) });
    const swatch = (label, col, outline) => ({ label, draw: (xx, yy) => kg.append("rect").attr("x", xx).attr("y", yy - 5)
      .attr("width", 7).attr("height", 5.4).attr("rx", 0.6).attr("fill", col).attr("stroke", outline || null).attr("stroke-width", 0.6) });
    rowKey(0, "role (a)", ["primary", "secondary", "rival", "tool"].map(glyph));
    rowKey(10.5, "outcome", [swatch("supported", OUT.supported), swatch("mixed", OUT.mixed), swatch("refuted or failed", OUT.refuted)]);
    rowKey(21, "", [swatch("untested", OUT.untested), swatch("reserved data", "url(#reserved)"),
      swatch("descriptive", "#fff", C.muted)]);
  },
};
