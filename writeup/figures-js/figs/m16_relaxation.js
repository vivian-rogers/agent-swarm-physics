// Model 16 (Langevin relaxation): a fast read kick on a slow, overdamped well. Single column.
// (a) H125 kickoff day profile; (b) H130 #51 own well vs read kick; (c) simulation x = s + k.
// Data: data/processed/paper-figs/m16_relaxation.json (export/m16_relaxation.py).
window.FIG = {
  width: 3.40, height: 3.12,
  draw(svg, D) {
    const { C, F, SZ } = S;
    const W = 3.40 * 72, H = 3.12 * 72;
    const g = svg.append("g");
    const fmt = (d, p = 3) => (d < 0 ? "−" : "+") + Math.abs(d).toFixed(p);

    // ------------------------------------------------------------------ (a) kickoff response
    const A = { x: 31, y: 18, w: W - 31 - 3, h: 66 };
    S.panel(g, 0, 8, "a", "After a kickoff: one overshoot, no undershoot");
    const ga = g.append("g").attr("transform", `translate(${A.x},${A.y})`);
    const xa = d3.scaleLinear().domain([0.45, 10.55]).range([0, A.w]);
    const ya = d3.scaleLinear().domain([-0.042, 0.092]).range([A.h, 0]);
    ga.append("rect").attr("x", xa(1.5)).attr("width", xa(3.5) - xa(1.5)).attr("y", 0).attr("height", A.h).attr("fill", C.nullBand);
    S.text(ga, (xa(1.5) + xa(3.5)) / 2, 7, "undershoot", { anchor: "middle", size: SZ.small, fill: C.ink2 });
    S.text(ga, (xa(1.5) + xa(3.5)) / 2, 14, "window", { anchor: "middle", size: SZ.small, fill: C.ink2 });
    S.axis(ga.append("g").attr("transform", `translate(0,${A.h})`), xa, "bottom",
      { ticks: d3.range(1, 11), format: (d) => d, title: "active day after the kickoff", titleOffset: 11 });
    S.axis(ga, ya, "left", { ticks: [-0.03, 0, 0.03, 0.06], format: (d) => (d === 0 ? "0" : d3.format(".2f")(d).replace("-", "−")),
      grid: true, length: A.w, title: "excess alignment", titleOffset: 23 });
    ga.append("line").attr("x1", 0).attr("x2", A.w).attr("y1", ya(0)).attr("y2", ya(0)).attr("stroke", C.muted).attr("stroke-width", 0.6);
    const series = [
      { key: "gte", col: C.muted, off: 0.12, dash: "2.2,1.4", shape: d3.symbolSquare, fill: "#fff", sw: 0.8, size: 9 },
      { key: "bge", col: C.field, off: -0.12, dash: null, shape: d3.symbolCircle, fill: C.field, sw: 0.6, size: 11 },
    ];
    for (const s of series) {
      const P = D.profile[s.key];
      ga.append("path").attr("d", d3.line().x((p) => xa(p.day + s.off)).y((p) => ya(p.m))(P))
        .attr("fill", "none").attr("stroke", s.col).attr("stroke-width", s.key === "bge" ? 1.2 : 0.9).attr("stroke-dasharray", s.dash);
      for (const p of P) {
        ga.append("line").attr("x1", xa(p.day + s.off)).attr("x2", xa(p.day + s.off)).attr("y1", ya(p.lo)).attr("y2", ya(p.hi))
          .attr("stroke", s.col).attr("stroke-width", 0.7);
        ga.append("path").attr("d", S.sym(s.shape, s.size)).attr("transform", `translate(${xa(p.day + s.off)},${ya(p.m)})`)
          .attr("fill", s.fill).attr("stroke", s.key === "bge" ? "#fff" : s.col).attr("stroke-width", s.sw);
      }
    }
    // labels + U
    S.legend(ga, xa(3.75), 7, [
      { label: "bge", color: C.field, size: 11 },
      { label: "gte", color: C.muted, fill: "#fff", stroke: C.muted, sw: 0.8, shape: d3.symbolSquare, size: 9 },
    ], { gap: 8 });
    const u = D.U;
    S.text(ga, A.w, 7, `$U$ = ${fmt(u.U)} [${fmt(u.lo)}, ${fmt(u.hi)}]`, { anchor: "end", size: SZ.small, fill: C.ink });
    S.text(ga, A.w, 14, `bge, ${u.k} kickoffs, 90% CI`, { anchor: "end", size: SZ.small, fill: C.ink2 });

    // ------------------------------------------------------------------ (b) well vs kick
    const top2 = A.y + A.h + 32;
    const B = { x: 31, y: top2 + 9, w: 126, h: 78 };
    S.panel(g, 0, top2, "b", "#51: two decay rates");
    const gb = g.append("g").attr("transform", `translate(${B.x},${B.y})`);
    const xb = d3.scaleSymlog().constant(1).domain([0, 1500]).range([4, B.w]);
    const yb = d3.scaleLinear().domain([-0.12, 1.6]).range([B.h, 0]);
    S.axis(gb.append("g").attr("transform", `translate(0,${B.h})`), xb, "bottom",
      { ticks: [0, 1, 10, 100, 1000], format: (d) => d, title: "lag (calls of the reader)", titleOffset: 11 });
    S.axis(gb, yb, "left", { ticks: [0, 0.5, 1, 1.5], format: (d) => (d === 0 ? "0" : d3.format(".1f")(d).replace(".0", "")), grid: true,
      length: B.w, title: "response / amplitude", titleOffset: 17 });
    gb.append("line").attr("x1", 0).attr("x2", B.w).attr("y1", yb(0)).attr("y2", yb(0)).attr("stroke", C.muted).attr("stroke-width", 0.6);
    const xs = d3.range(0, 1, 0.02).concat(d3.range(0, 3.18, 0.01).map((e) => 10 ** e));
    for (const [gam, col] of [[D.g_well, C.field], [D.g_kick, C.coupling]])
      gb.append("path").attr("d", d3.line().x((t) => xb(t)).y((t) => yb(Math.exp(-gam * t)))(xs))
        .attr("fill", "none").attr("stroke", col).attr("stroke-width", 0.9).attr("opacity", 0.9);
    for (const p of D.well) S.pointCI(gb, xb(p.lag), yb(p.y), null, null, { color: C.field, size: 12 });
    for (const p of D.kick) S.pointCI(gb, xb(p.lag), yb(p.y), yb(p.y - p.se), yb(p.y + p.se),
      { color: C.coupling, shape: d3.symbolSquare, size: 10 });
    S.halo(S.text(gb, xb(0.25), yb(0.36), "read kick", { size: SZ.small, fill: C.coupling }));
    S.halo(S.text(gb, xb(0.25), yb(0.36) + 7.2, `≈ ${D.t_kick} calls`, { size: SZ.small, fill: C.coupling }));
    S.halo(S.text(gb, xb(150), yb(0.72), "own well", { size: SZ.small, fill: "#a86f00" }));
    S.halo(S.text(gb, xb(150), yb(0.72) + 7.2, `≈ ${D.t_well} calls`, { size: SZ.small, fill: "#a86f00" }));
    const r = D.rho, rc = D.rho_ci90;
    S.text(gb, B.w, 5, `$ρ_{γ}$ = ${r.toFixed(1)}`, { anchor: "end", size: SZ.small, fill: C.ink });
    S.text(gb, B.w, 12.5, `[${rc[0].toFixed(1)}, ${rc[1].toFixed(1)}] (90%)`, { anchor: "end", size: SZ.small, fill: C.ink2 });

    // ------------------------------------------------------------------ (c) simulation
    const Cx = 176, Cc = { x: Cx, y: B.y, w: W - Cx - 7, h: B.h };
    S.panel(g, Cx - 10, top2, "c", "Simulation");
    const gc = g.append("g").attr("transform", `translate(${Cc.x},${Cc.y})`);
    const sim = D.sim, n = sim.x.length;
    const lo = Math.min(d3.min(sim.x), d3.min(sim.s)), hi = Math.max(d3.max(sim.x), d3.max(sim.s)), span = hi - lo;
    const xc = d3.scaleLinear().domain([0, n]).range([0, Cc.w]);
    const yc = d3.scaleLinear().domain([lo - 0.30 * span, hi + 0.22 * span]).range([Cc.h, 0]);
    S.axis(gc.append("g").attr("transform", `translate(0,${Cc.h})`), xc, "bottom",
      { ticks: [0, 200, 400], format: (d) => d, title: "call", titleOffset: 11 });
    S.text(gc, -4, Cc.h / 2, "state (a.u.)", { anchor: "middle", rotate: -90, size: SZ.label });
    gc.append("line").attr("x1", 0).attr("x2", 0).attr("y1", 0).attr("y2", Cc.h).attr("stroke", C.ink2).attr("stroke-width", 0.5);
    const idx = d3.range(n);
    gc.append("path").attr("d", d3.line().x((i) => xc(i)).y((i) => yc(sim.x[i]))(idx)).attr("fill", "none")
      .attr("stroke", C.coupling).attr("stroke-width", 0.8).attr("stroke-linejoin", "round");
    gc.append("path").attr("d", d3.line().x((i) => xc(i)).y((i) => yc(sim.s[i]))(idx)).attr("fill", "none")
      .attr("stroke", C.field).attr("stroke-width", 1.0).attr("stroke-linejoin", "round");
    const yt = yc(lo - 0.12 * span);
    for (const rd of sim.reads) gc.append("line").attr("x1", xc(rd)).attr("x2", xc(rd)).attr("y1", yt).attr("y2", yt + 5)
      .attr("stroke", C.ink2).attr("stroke-width", 0.7);
    S.text(gc, xc(sim.reads[0]) - 2.5, yt + 4.4, "reads", { anchor: "end", size: SZ.small, fill: C.ink2 });
        S.text(gc, 3, 6, "state $x$ = $s$ + kicks", { size: SZ.small, fill: C.coupling });
    S.halo(S.text(gc, xc(112), yc(d3.min(sim.s.slice(85, 140))) + 8, "well $s$", { anchor: "middle", size: SZ.small, fill: "#a86f00" }));
  },
};
