// Sec. IV (models 02 and 09, H111): a sum rule that links talk fluctuations to the read-out gain.
// (a) simulated linear Hawkes talk swarm: Fano ratio vs loop gain, with the sum-rule curve (no free parameter);
// (b) village units: observed vs predicted Fano ratio of 10-min talk counts, by regime, with pooled r_F.
// Data: data/processed/paper-figs/h111_fano.json (export/h111_fano.py).
window.FIG = {
  width: 3.40, height: 4.12,
  draw(svg, D) {
    const { C, SZ, REG, REG_SHAPE } = S;
    const W = 3.40 * 72;
    const g = svg.append("g");
    const defs = svg.append("defs");
    const f1 = d3.format(".1f"), f2 = d3.format(".2f");

    // ------------------------------------------------------------------ (a) simulation
    const A = { x: 27, y: 18, w: W - 27 - 4, h: 86 };
    S.panel(g, 0, 8, "a", "Simulation: the Fano ratio follows the gain");
    const ga = g.append("g").attr("transform", `translate(${A.x},${A.y})`);
    const xa = d3.scaleLinear().domain([-0.02, 0.63]).range([0, A.w]);
    const ya = d3.scaleLinear().domain([0.6, 5.6]).range([A.h, 0]);
    defs.append("clipPath").attr("id", "h111a").append("rect").attr("x", 0).attr("y", 0).attr("width", A.w).attr("height", A.h);

    // village regime-III gain range (H67 gains of the 18 units of panel b)
    const g3 = D.units.filter((d) => d.regime === "III").map((d) => d.g);
    const [gl, gh] = d3.extent(g3);
    ga.append("rect").attr("x", xa(Math.max(gl, 0))).attr("width", xa(gh) - xa(Math.max(gl, 0))).attr("y", 0).attr("height", A.h)
      .attr("fill", C.coupling).attr("opacity", 0.08);
    S.text(ga, (xa(Math.max(gl, 0)) + xa(gh)) / 2, 8, "village regime III", { anchor: "middle", size: SZ.small, fill: C.coupling });
    S.text(ga, (xa(Math.max(gl, 0)) + xa(gh)) / 2, 15.5, `$g$ = ${f2(Math.max(gl, 0))}–${f2(gh)}`, { anchor: "middle", size: SZ.small, fill: C.coupling });

    S.axis(ga.append("g"), ya, "left", { ticks: [1, 2, 3, 4, 5], format: d3.format("d"), grid: true, length: A.w,
      title: "Fano ratio Φ", titleOffset: 15 });
    S.axis(ga.append("g").attr("transform", `translate(0,${A.h})`), xa, "bottom",
      { ticks: [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6], format: f1, title: "loop gain $g$ set in the simulation", titleOffset: 10.5 });

    // no-coupling band (95% of g = 0 runs)
    const nb = D.sim.null_band;
    ga.append("rect").attr("x", 0).attr("width", A.w).attr("y", ya(nb[1])).attr("height", ya(nb[0]) - ya(nb[1]))
      .attr("fill", C.null).attr("opacity", 0.55);
    S.halo(S.text(ga, A.w - 2, ya(nb[1]) - 2.5, "no coupling: 95% of runs", { anchor: "end", size: SZ.small, fill: C.ink2 }));

    const cg = ga.append("g").attr("clip-path", "url(#h111a)");
    const cv = D.sim.curve;
    cg.append("path").datum(cv).attr("d", d3.line().x((d) => xa(d.g)).y((d) => ya(d.plain)))
      .attr("fill", "none").attr("stroke", C.ink2).attr("stroke-width", 0.9).attr("stroke-dasharray", "1.2,1.6");
    cg.append("path").datum(cv).attr("d", d3.line().x((d) => xa(d.g)).y((d) => ya(d.rule)))
      .attr("fill", "none").attr("stroke", C.ink).attr("stroke-width", 1.3);
    for (const p of D.sim.points) S.pointCI(ga, xa(p.g), ya(p.mean), ya(p.lo), ya(p.hi),
      { color: C.coupling, fill: "#fff", stroke: C.coupling, sw: 0.9, size: 11 });

    // direct labels, set along the curves
    const at = (x, key) => { const d = cv.reduce((a, b) => Math.abs(b.g - x) < Math.abs(a.g - x) ? b : a); return d[key]; };
    const angA = (x, key) => Math.atan2(ya(at(x + 0.02, key)) - ya(at(x - 0.02, key)), xa(x + 0.02) - xa(x - 0.02)) * 180 / Math.PI;
    const along = (x, key, dy, str, col) => {
      const px = xa(x), py = ya(at(x, key)), a = angA(x, key), r = a * Math.PI / 180;
      const tx = px - dy * Math.sin(r), ty = py + dy * Math.cos(r);
      S.halo(S.text(ga, tx, ty, str, { anchor: "middle", size: SZ.small, fill: col, rotate: a }));
    };
    along(0.25, "rule", 7.5, "sum rule", C.ink);
    along(0.47, "plain", -2.5, "1/(1 − $g$)^{2}", C.ink2);
    S.halo(S.text(ga, xa(0.4) - 4, ya(2.3) + 10, `simulated: ${D.sim.n} agents, ${D.sim.runs} runs`, { size: SZ.small, fill: C.coupling }));

    // ------------------------------------------------------------------ (b) village
    const B = { x: 27, y: 146, w: W - 27 - 4, h: 132 };
    S.panel(g, 0, B.y - 10, "b", "Village: regime III sits on the prediction");
    const gb = g.append("g").attr("transform", `translate(${B.x},${B.y})`);
    const xb = d3.scaleLinear().domain([0.82, 2.1]).range([0, B.w]);
    const yb = d3.scaleLinear().domain([0.45, 2.55]).range([B.h, 0]);
    defs.append("clipPath").attr("id", "h111b").append("rect").attr("x", 0).attr("y", 0).attr("width", B.w).attr("height", B.h);
    const cb = gb.append("g").attr("clip-path", "url(#h111b)");

    // independent-agent null: below its 95th percentile (median over units)
    cb.append("rect").attr("x", 0).attr("width", B.w).attr("y", yb(D.null_q95_median)).attr("height", B.h - yb(D.null_q95_median))
      .attr("fill", C.nullBand).attr("opacity", 0.75);
    // +-20% band and the diagonal
    const xs = [0.82, 2.1];
    cb.append("path").attr("d", d3.area().x((d) => xb(d)).y0((d) => yb(0.8 * d)).y1((d) => yb(1.2 * d))(xs))
      .attr("fill", C.coupling).attr("opacity", 0.08);
    S.axis(gb.append("g"), yb, "left", { ticks: [0.5, 1, 1.5, 2, 2.5], format: f1, title: "observed Φ (10 min)", titleOffset: 18 });
    S.axis(gb.append("g").attr("transform", `translate(0,${B.h})`), xb, "bottom",
      { ticks: [1, 1.2, 1.4, 1.6, 1.8, 2], format: f1, title: "predicted Φ_{pred} from the read-out gain (H67)", titleOffset: 10.5 });

    const order = ["I", "II", "III"];
    const ciOp = { I: 0.35, II: 0.45, III: 0.6 };
    for (const r of order) {
      const us = D.units.filter((d) => d.regime === r);
      for (const u of us) {
        cb.append("line").attr("x1", xb(u.pred)).attr("x2", xb(u.pred)).attr("y1", yb(u.obs_lo)).attr("y2", yb(u.obs_hi))
          .attr("stroke", REG[r]).attr("stroke-width", 0.6).attr("opacity", ciOp[r]);
        cb.append("line").attr("y1", yb(u.obs)).attr("y2", yb(u.obs)).attr("x1", xb(u.pred_lo)).attr("x2", xb(u.pred_hi))
          .attr("stroke", REG[r]).attr("stroke-width", 0.6).attr("opacity", ciOp[r]);
      }
    }
    cb.append("line").attr("x1", xb(0.82)).attr("x2", xb(2.1)).attr("y1", yb(0.82)).attr("y2", yb(2.1))
      .attr("stroke", C.ink).attr("stroke-width", 1.0);
    for (const r of order) for (const u of D.units.filter((d) => d.regime === r))
      S.pointCI(gb, xb(u.pred), yb(u.obs), null, null, { color: REG[r], shape: REG_SHAPE[r], size: r === "III" ? 13 : 11, sw: 0.5 });

    // line and band labels
    const ang = Math.atan2(yb(2) - yb(1), xb(2) - xb(1)) * 180 / Math.PI;
    const lx = 1.86, ly = 1.86;
    S.halo(S.text(gb, xb(lx), yb(ly) - 2.5, "observed = predicted", { anchor: "middle", size: SZ.small, fill: C.ink, rotate: ang }));
    const ux = 1.72, uy = 1.2 * 1.72;
    S.text(gb, xb(ux), yb(uy) + 7, "±20%", { anchor: "middle", size: SZ.small, fill: C.coupling, rotate: Math.atan2(yb(1.2 * 2) - yb(1.2), xb(2) - xb(1)) * 180 / Math.PI });
    S.text(gb, B.w - 3, yb(D.null_q95_median) + 7.5, "independent agents", { anchor: "end", size: SZ.small, fill: C.ink2 });
    S.text(gb, B.w - 3, yb(D.null_q95_median) + 14.5, "fall here (95%)", { anchor: "end", size: SZ.small, fill: C.ink2 });

    // key with pooled r_F (lower right, below the diagonal)
    const k = gb.append("g").attr("transform", `translate(${xb(1.31)},${yb(0.83)})`);
    const rows = [
      { r: "III", t: `regime III, ${D.n.III} units: $r_{F}$ = ${f2(D.rF_III[0])} [${f2(D.rF_III[1])}, ${f2(D.rF_III[2])}]` },
      { r: "I", t: `regime I, ${D.n.I} units: $r_{F}$ = ${f2(D.rF_I[0])} [${f2(D.rF_I[1])}, ${f2(D.rF_I[2])}]` },
      { r: "II", t: `regime II, ${D.n.II} units` },
    ];
    rows.forEach((row, i) => {
      const yy = i * 8.6;
      k.append("path").attr("d", S.sym(REG_SHAPE[row.r], 12)).attr("transform", `translate(2,${yy - 2})`)
        .attr("fill", REG[row.r]).attr("stroke", "#fff").attr("stroke-width", 0.5);
      S.halo(S.text(k, 7, yy, row.t, { size: SZ.small, fill: row.r === "II" ? C.ink2 : REG[row.r] }));
    });
  },
};
