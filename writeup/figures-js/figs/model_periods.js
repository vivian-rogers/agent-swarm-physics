// Where each physics model was tested: rows = models (primary model of each card, paper order), columns = goal
// periods by regime and natural experiments. Each cell is a small stacked bar of the verdicts of that model's cards
// in that period (height grows with the number of tests). Data: hyp_grid.json (export/hyp_grid.py).
window.FIG = {
  width: 7.05, height: 3.55, data: "hyp_grid",
  draw(svg, D) {
    const { C } = S;
    const W = 7.05 * 72, H = 3.55 * 72;
    const g = svg.append("g");
    const ORDER = ["02", "09", "11", "01", "16", "17", "04", "03", "15", "14", "08", "06", "10", "13"];
    const TIER = { "02": "useful", "09": "useful", "11": "useful", "01": "useful", "16": "useful", "17": "useful",
      "04": "partly", "03": "partly", "15": "partly", "14": "partly", "08": "partly", "06": "not", "10": "not", "13": "not" };
    const VC = { supported: C.green, mixed: "#9a9a9a", other: "#9a9a9a", failed: C.up, descriptive: "#cfcfcf" };
    const VORD = ["supported", "mixed", "descriptive", "failed"];
    const model = new Map(D.rows.map((r) => [r.id, r.model || ""]));
    const ncards = d3.rollup(D.rows, (v) => v.length, (r) => r.model || "");
    const P = D.periods, pidx = new Map(P.map((p, i) => [p.id, i]));
    // counts[model][period][verdict]
    const cnt = new Map(ORDER.map((m) => [m, P.map(() => ({}))]));
    for (const c of D.cells) {
      if (c.v === "n/a" || c.v === "pending") continue;
      const m = model.get(c.h); if (!cnt.has(m)) continue;
      const v = c.v === "other" ? "mixed" : c.v;
      const o = cnt.get(m)[pidx.get(c.p)]; o[v] = (o[v] || 0) + 1;
    }
    const tot = (o) => d3.sum(Object.values(o));
    const maxN = d3.max(ORDER, (m) => d3.max(cnt.get(m), tot));

    const L = 118, R = 64, top = 46, rowH = (H - top - 26) / ORDER.length;
    const colW = (W - L - R) / P.length, x = (i) => L + i * colW;
    const hScale = (n) => (rowH - 2.2) * Math.sqrt(n / maxN);

    // reserved shading, regime bands, column labels
    P.forEach((p, i) => { if (p.reserved) g.append("rect").attr("x", x(i)).attr("y", top - 2).attr("width", colW)
      .attr("height", rowH * ORDER.length + 2).attr("fill", "#f3ece0"); });
    const bands = d3.groups(P.map((p, i) => ({ ...p, i })), (p) => p.kind === "NE" ? "NE" : p.regime);
    for (const [k, ps] of bands) {
      const i0 = d3.min(ps, (p) => p.i), i1 = d3.max(ps, (p) => p.i) + 1;
      const col = k === "NE" ? C.ink2 : S.REG[k] || C.muted;
      g.append("rect").attr("x", x(i0) + 0.4).attr("y", top - 6).attr("width", x(i1) - x(i0) - 0.8).attr("height", 2).attr("fill", col);
      S.text(g, (x(i0) + x(i1)) / 2, top - 30, k === "NE" ? "natural experiments" : `regime ${k}`, { anchor: "middle", size: 6.4, fill: col });
    }
    P.forEach((p, i) => {
      g.append("text").attr("transform", `translate(${x(i) + colW / 2 + 1.8},${top - 8}) rotate(-90)`)
        .attr("font-family", S.F.tick).attr("font-size", 5.4).attr("fill", C.ink2)
        .text(p.kind === "NE" ? p.id : p.id.replace(/^G0?/, ""));
    });

    // rows
    ORDER.forEach((m, r) => {
      const y0 = top + r * rowH, yb = y0 + rowH - 0.8;
      if (r > 0 && TIER[m] !== TIER[ORDER[r - 1]]) g.append("line").attr("x1", 0).attr("x2", W).attr("y1", y0).attr("y2", y0)
        .attr("stroke", C.rule).attr("stroke-width", 0.5);
      g.append("line").attr("x1", L).attr("x2", W - R).attr("y1", yb).attr("y2", yb).attr("stroke", C.grid).attr("stroke-width", 0.4);
      const t = g.append("text").attr("x", 0).attr("y", y0 + rowH * 0.62).attr("font-size", 6.6).attr("fill", C.ink);
      t.append("tspan").attr("font-family", S.F.bold).text(m);
      t.append("tspan").attr("font-family", S.F.body).attr("dx", 3).text(D.names[m]);
      t.append("tspan").attr("font-family", S.F.tick).attr("font-size", 5.6).attr("fill", C.muted).attr("dx", 3)
        .text(`${ncards.get(m) || 0} card${(ncards.get(m) || 0) > 1 ? "s" : ""}`);
      let nT = 0, nPer = 0;
      cnt.get(m).forEach((o, i) => {
        const n = tot(o); if (!n) return;
        nT += n; if (P[i].kind === "G") nPer += 1;
        const h = hScale(n); let yy = yb;
        for (const v of VORD) {
          const k = o[v] || 0; if (!k) continue;
          const hh = h * k / n;
          g.append("rect").attr("x", x(i) + 0.55).attr("y", yy - hh).attr("width", colW - 1.1).attr("height", hh).attr("fill", VC[v]);
          yy -= hh;
        }
      });
      S.text(g, W - R + 5, y0 + rowH * 0.62, `${nT} tests, ${nPer} periods`, { size: 5.9, fill: C.ink2 });
    });
    // legend
    S.legend(g, L, H - 4, [
      { label: "supported", rect: true, color: VC.supported }, { label: "mixed or inconclusive", rect: true, color: VC.mixed },
      { label: "descriptive", rect: true, color: VC.descriptive }, { label: "failed", rect: true, color: VC.failed },
      { label: "reserved period", rect: true, color: "#f3ece0" },
    ], { gap: 10, size: 6.2 });
    S.text(g, W - R + 5, H - 4, `bar height ∝ √(tests); max ${maxN}`, { size: 5.6, fill: C.muted });
  },
};
