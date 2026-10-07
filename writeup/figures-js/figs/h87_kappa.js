// The kappa table (model 04, H87): per channel, bits about where to work (a), output value lost (b), value per bit (c).
// Data: data/processed/paper-figs/h87_kappa.json (export/h87_kappa.py).
window.FIG = {
  width: 7.05, height: 2.12,
  draw(svg, D) {
    const { C } = S;
    const W = 7.05 * 72, H = 2.12 * 72;
    const g = svg.append("g");
    const ERASE = C.vermillion;                   // forced erasure of the context window (as in fig:erasure)
    const rows = D.rows;
    const col = (r) => r.code === "C" ? ERASE : r.identified ? C.ink2 : "#a3a3a3";

    // ---- layout: row labels, then three forest panels sharing the rows
    const top = 27, rowH = 13.2, nR = rows.length;
    const plotH = nR * rowH;
    const yRow = (i) => top + (i + 0.5) * rowH;
    const labW = 70, gap = 20, x0 = labW + 8;
    const pw = (W - x0 - 2 - 2 * gap) / 3;
    const P = [0, 1, 2].map((k) => x0 + k * (pw + gap));

    // row labels + faint row guides across all panels
    rows.forEach((r, i) => {
      S.text(g, labW, yRow(i), r.name, { anchor: "end", baseline: "middle", size: 7.2,
        fill: r.code === "C" ? ERASE : r.identified ? C.ink : C.ink2 });
      for (const px of P) g.append("line").attr("x1", px).attr("x2", px + pw).attr("y1", yRow(i)).attr("y2", yRow(i))
        .attr("stroke", "#f0f0f0").attr("stroke-width", 0.5);
    });

    function frame(k, letter, title, dom, ticks, xtitle, fmt) {
      const x = d3.scaleLinear().domain(dom).range([0, pw]);
      const gp = g.append("g").attr("transform", `translate(${P[k]},0)`);
      S.panel(g, k === 0 ? 0 : P[k], 9, letter, title);
      const ax = gp.append("g").attr("transform", `translate(0,${top + plotH + 3})`);
      S.axis(ax, x, "bottom", { ticks, format: fmt || ((d) => d), title: xtitle, titleOffset: 13 });
      return { x, gp };
    }
    const zero = (f) => f.gp.append("line").attr("x1", f.x(0)).attr("x2", f.x(0)).attr("y1", top - 2)
      .attr("y2", top + plotH + 3).attr("stroke", C.ink2).attr("stroke-width", 0.5);
    const ci = (f, i, lo, hi, c, clipLo) => {
      const y = yRow(i);
      f.gp.append("line").attr("x1", f.x(Math.max(lo, clipLo ?? -1e9))).attr("x2", f.x(hi)).attr("y1", y).attr("y2", y)
        .attr("stroke", c).attr("stroke-width", 0.9).attr("stroke-linecap", "round");
      if (clipLo != null && lo < clipLo) {            // interval runs off the axis: small arrowhead
        const xa = f.x(clipLo);
        f.gp.append("path").attr("d", `M${xa - 0.5},${y}l3.4,-1.9v3.8z`).attr("fill", c);
      }
    };
    const pt = (f, i, v, c) => f.gp.append("circle").attr("cx", f.x(v)).attr("cy", yRow(i)).attr("r", 2.1)
      .attr("fill", c).attr("stroke", "#fff").attr("stroke-width", 0.6);
    const fmt2 = (d) => d === 0 ? "0" : d3.format(".2~f")(d).replace("-", "−");

    // ---------------------------------------------------------------- (a) bits
    const A = frame(0, "a", "Bits about where to work", [-0.05, 0.82], [0, 0.25, 0.5, 0.75], "$I_{c}$ (bits)", fmt2);
    A.gp.insert("rect", ":first-child").attr("x", A.x(-0.05)).attr("width", A.x(D.floor) - A.x(-0.05))
      .attr("y", top - 2).attr("height", plotH + 5).attr("fill", C.nullBand);
    S.text(A.gp, A.x(D.floor) + 2.5, top - 4, "below 0.02 bits: not identified", { size: 6.0, fill: C.muted });
    rows.forEach((r, i) => {
      const c = col(r);
      if (r.I_ci == null) {                          // human messages name no repository: zero bits by construction
        const xx = A.x(0), y = yRow(i);
        A.gp.append("path").attr("d", `M${xx - 1.8},${y - 1.8}L${xx + 1.8},${y + 1.8}M${xx - 1.8},${y + 1.8}L${xx + 1.8},${y - 1.8}`)
          .attr("stroke", c).attr("stroke-width", 0.8);
        S.text(A.gp, xx + 5, y, "0: names no repository", { baseline: "middle", size: 6.2, fill: C.muted });
        return;
      }
      ci(A, i, r.I_ci[0], r.I_ci[1], c);
      pt(A, i, r.I, c);
    });
    const rC = rows[0];
    S.text(A.gp, A.x(rC.I_ci[1]) + 3, yRow(0), d3.format(".3f")(rC.I), { baseline: "middle", size: 6.4, fill: ERASE });

    // ---------------------------------------------------------------- (b) value
    const LO = -0.62;
    const B = frame(1, "b", "Output value lost", [LO, 0.56], [-0.5, -0.25, 0, 0.25, 0.5],
      "Δ$V_{c}$ (commits per 20 calls)", fmt2);
    zero(B);
    rows.forEach((r, i) => { const c = col(r); ci(B, i, r.dV_ci[0], r.dV_ci[1], c, LO); pt(B, i, r.dV, c); });
    S.text(B.gp, B.x(rC.dV_ci[0]) - 3, yRow(0), d3.format(".2f")(rC.dV), { anchor: "end", baseline: "middle", size: 6.4, fill: ERASE });

    // ---------------------------------------------------------------- (c) value per bit
    const K = frame(2, "c", "Value per bit", [-2.4, 9], [0, 2, 4, 6, 8], "$𝜅_{c}$ (commits per 20 calls per bit)",
      (d) => String(d));
    zero(K);
    rows.forEach((r, i) => {
      const c = col(r);
      if (r.k == null) {
        S.text(K.gp, K.x(3.3), yRow(i), "n.i.", { anchor: "middle", baseline: "middle", size: 6.4, fill: C.muted });
        return;
      }
      ci(K, i, r.k_ci[0], r.k_ci[1], c);
      pt(K, i, r.k, c);
    });
    const f1 = d3.format(".1f");
    S.text(K.gp, K.x(rC.k), yRow(0) - 5, `${f1(rC.k)} [${f1(rC.k_ci[0])}, ${f1(rC.k_ci[1])}]`,
      { anchor: "middle", size: 6.4, fill: ERASE });
    const rA = rows[1];
    S.text(K.gp, K.x(rA.k_ci[1]) + 3, yRow(1), f1(rA.k).replace("-", "−"), { baseline: "middle", size: 6.4, fill: C.ink2 });
  },
};
