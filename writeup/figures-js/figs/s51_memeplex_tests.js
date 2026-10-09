// Paper 2, Sec. results: the memeplexes of goal period 51 against the conditions of the definition (Fig. fig:tests).
// One row per memeplex (H145's frozen K01-K15; K14 left out: 4 elements, 3 hosts, nearly empty comparison sets).
// Five panels, one condition each. Gray = matched random element sets (pseudo-patterns); green = the condition is met
// beyond them; red = the pattern harms its hosts beyond them. Data: s51_memeplex_tests.json (export/s51_memeplex_tests.py).
window.FIG = {
  width: 7.05, height: 2.62,
  draw(svg, D) {
    const { C, SZ } = S;
    const W = 7.05 * 72, H = 2.62 * 72;
    const g = svg.append("g");
    const GOOD = "#0ca30c", BAD = "#d03b3b", NEUTRAL = C.ink2, PSEUDO = "#c8c8c8";
    const rows = D.rows.filter((r) => r.id !== "K14");
    if (rows.length !== 14) throw new Error("expected 14 rows, got " + rows.length);

    // ------------------------------------------------------------------ layout
    const LM = 74, RM = 4, GAP = 13, TOP = 24, BOT = 30;
    const nP = 5, pw = (W - LM - RM - GAP * (nP - 1)) / nP;
    const pitch = (H - TOP - BOT) / rows.length;
    const yOf = (i) => TOP + pitch * (i + 0.5);
    const px = (k) => LM + k * (pw + GAP);

    // row labels
    for (const [i, r] of rows.entries()) {
      const t = g.append("text").attr("x", LM - 5).attr("y", yOf(i) + 2.1).attr("text-anchor", "end");
      t.append("tspan").attr("font-family", S.F.tick).attr("font-size", SZ.tick).attr("fill", C.ink2).text(r.id);
      if (r.label) t.append("tspan").attr("font-family", S.F.body).attr("font-size", SZ.small).attr("fill", C.ink).attr("dx", 3).text(r.label);
      if (i % 2 === 0) g.append("rect").attr("x", LM - 2).attr("y", yOf(i) - pitch / 2).attr("width", W - LM - RM + 2).attr("height", pitch)
        .attr("fill", "#f5f5f5").lower();
    }

    const panelAxis = (k, scale, ticks, fmt, title) => {
      const gp = g.append("g").attr("transform", `translate(${px(k)},${H - BOT})`);
      S.axis(gp, scale, "bottom", { ticks, format: fmt, title, titleOffset: 9.5 });
      return gp;
    };
    const vline = (k, scale, v, o = {}) => g.append("line").attr("x1", px(k) + scale(v)).attr("x2", px(k) + scale(v))
      .attr("y1", TOP - 2).attr("y2", H - BOT).attr("stroke", o.color || C.ink2).attr("stroke-width", 0.5)
      .attr("stroke-dasharray", o.dash ? "1.8,1.4" : null);
    const clipped = (scale, v) => Math.max(scale.range()[0] + 1.2, Math.min(scale.range()[1] - 1.2, scale(v)));
    const f2 = S.fmtMinus(d3.format(".1f")), f1 = S.fmtMinus(d3.format(".1f"));

    // ------------------------------------------------------------------ a: host renewal
    {
      const x = d3.scaleLinear().domain([-0.25, 0.1]).range([0, pw]);
      S.panel(g, px(0), 11, "a", "hosts turn over");
      panelAxis(0, x, [-0.2, -0.1, 0, 0.1], f1, "$D$_{K}(5) − null");
      vline(0, x, 0);
      for (const [i, r] of rows.entries()) {
        if (r.renew < x.domain()[0] || r.renew > x.domain()[1]) throw new Error("renew out of range " + r.id);
        g.append("rect").attr("x", px(0) + Math.min(x(0), x(r.renew))).attr("width", Math.abs(x(r.renew) - x(0)))
          .attr("y", yOf(i) - pitch * 0.32).attr("height", pitch * 0.64).attr("fill", r.renew_pass ? GOOD : PSEUDO);
      }
    }
    // ------------------------------------------------------------------ b: colonial A excess z
    {
      const x = d3.scaleLinear().domain([-2, 4]).range([0, pw]);
      S.panel(g, px(1), 11, "b", "predicts itself");
      panelAxis(1, x, [-2, 0, 2, 4], S.fmtMinus(d3.format("d")), "$z$ of colonial $A$");
      vline(1, x, 0); vline(1, x, 2, { dash: true });
      for (const [i, r] of rows.entries()) {
        if (r.A_z < -2 || r.A_z > 4) throw new Error("A_z out of range " + r.id);
        S.pointCIh(g, px(1) + x(r.A_z), yOf(i), null, null, { color: r.A_pass ? GOOD : NEUTRAL, size: 10 });
      }
    }
    // ------------------------------------------------------------------ c: re-expression after a wipe
    {
      const x = d3.scaleLinear().domain([0.5, 1.5]).range([0, pw]);
      S.panel(g, px(2), 11, "c", "survives a wipe");
      panelAxis(2, x, [0.5, 1, 1.5], f1, "wipe / placebo");
      vline(2, x, 1); vline(2, x, 0.5, { dash: true });
      for (const [i, r] of rows.entries()) {
        for (const v of r.wipe_pseudo) g.append("circle").attr("cx", px(2) + clipped(x, v)).attr("cy", yOf(i)).attr("r", 1.1).attr("fill", PSEUDO);
        S.pointCIh(g, px(2) + x(r.wipe), yOf(i), px(2) + clipped(x, r.wipe_ci[0]), px(2) + clipped(x, r.wipe_ci[1]),
          { color: r.wipe < 0.5 ? BAD : NEUTRAL, size: 10 });
      }
    }
    // ------------------------------------------------------------------ d: repair after a wipe
    {
      const x = d3.scaleLinear().domain([0.8, 1.25]).range([0, pw]);
      S.panel(g, px(3), 11, "d", "gets repaired");
      panelAxis(3, x, [0.8, 1, 1.2], f1, "wipe / placebo");
      vline(3, x, 1); vline(3, x, 1.2, { dash: true });
      for (const [i, r] of rows.entries()) {
        for (const v of r.repair_pseudo) g.append("circle").attr("cx", px(3) + clipped(x, v)).attr("cy", yOf(i)).attr("r", 1.1).attr("fill", PSEUDO);
        const pass = r.repair > 1.2 && r.repair_ci[0] > 1;
        S.pointCIh(g, px(3) + x(r.repair), yOf(i), px(3) + clipped(x, r.repair_ci[0]), px(3) + clipped(x, r.repair_ci[1]),
          { color: pass ? GOOD : NEUTRAL, size: 10 });
      }
    }
    // ------------------------------------------------------------------ e: cost to hosts
    {
      const x = d3.scaleLinear().domain([-0.4, 0.35]).range([0, pw]);
      S.panel(g, px(4), 11, "e", "costs its hosts");
      panelAxis(4, x, [-0.4, -0.2, 0, 0.2], f1, "Δ own commits");
      vline(4, x, 0);
      for (const [i, r] of rows.entries()) {
        g.append("rect").attr("x", px(4) + clipped(x, r.cost_band[0])).attr("width", clipped(x, r.cost_band[1]) - clipped(x, r.cost_band[0]))
          .attr("y", yOf(i) - pitch * 0.3).attr("height", pitch * 0.6).attr("fill", "#e4e4e4");
        const col = r.cost_class === "parasitic" ? BAD : r.cost_class === "mutualist" ? GOOD : NEUTRAL;
        S.pointCIh(g, px(4) + x(r.cost), yOf(i), px(4) + clipped(x, r.cost_ci[0]), px(4) + clipped(x, r.cost_ci[1]), { color: col, size: 10 });
      }
    }

    // ------------------------------------------------------------------ key
    S.legend(g, LM, H - 3, [
      { label: "matched random element sets", color: PSEUDO, size: 6 },
      { label: "memeplex", color: NEUTRAL, size: 9 },
      { label: "condition met beyond the random sets", color: GOOD, size: 9 },
      { label: "harms its hosts beyond them", color: BAD, size: 9 },
    ], { size: SZ.small });
  },
};
