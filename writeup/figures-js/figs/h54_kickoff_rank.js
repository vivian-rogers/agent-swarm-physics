// Sec. IV (model 11, H54): the own kickoff text is the target.
// (a) rank of each period's own kickoff among the 33 candidates (bge), against the kickoff-swap null;
// (b) #51 private goals: weekly share of pairs where an agent's content matches its own goal better than a swapped one.
// Data: data/processed/paper-figs/h54_kickoff_rank.json (export/h54_kickoff_rank.py).
window.FIG = {
  width: 3.40, height: 3.09,
  draw(svg, D) {
    const { C, SZ } = S;
    const W = 3.40 * 72;
    const g = svg.append("g");
    const FIELD_INK = "#9a6500";

    // ------------------------------------------------------------------ (a) rank of the own kickoff
    const A = { x: 30, y: 17, w: W - 30 - 4, h: 92 };
    S.panel(g, 0, 8, "a", "Day 1 of each goal period ranks its own kickoff first");
    const ga = g.append("g").attr("transform", `translate(${A.x},${A.y})`);
    const P = D.periods;
    const xa = d3.scalePoint().domain(P.map((d) => d.goal)).range([3, A.w - 3]);
    const ya = d3.scaleLog().domain([0.82, D.n + 4]).range([0, A.h]);

    // swap null: 90% band and median
    ga.append("rect").attr("x", 0).attr("width", A.w).attr("y", ya(D.null_band[0])).attr("height", ya(D.null_band[1]) - ya(D.null_band[0]))
      .attr("fill", C.nullBand).attr("opacity", 0.8);
    ga.append("line").attr("x1", 0).attr("x2", A.w).attr("y1", ya(D.null_median)).attr("y2", ya(D.null_median))
      .attr("stroke", C.muted).attr("stroke-width", 0.8).attr("stroke-dasharray", "3,2");
    S.axis(ga.append("g"), ya, "left", { ticks: [1, 2, 5, 10, 20, 33], format: d3.format("d"),
      title: "rank of own kickoff", titleOffset: 18 });
    ga.append("line").attr("x1", 0).attr("x2", A.w).attr("y1", A.h).attr("y2", A.h).attr("stroke", C.ink2).attr("stroke-width", 0.5);

    // points
    for (const p of P) {
      if (p.free) S.pointCI(ga, xa(p.goal), ya(p.rank), null, null,
        { shape: d3.symbolSquare, size: 11, fill: "#fff", stroke: C.ink2, sw: 0.8 });
      else S.pointCI(ga, xa(p.goal), ya(p.rank), null, null, { color: C.field, size: 14, stroke: C.ink, sw: 0.45 });
    }
    // null and result labels
    S.halo(S.text(ga, xa(4), ya(D.null_median) - 2.5, `swap null: median ${D.null_median}, 90% band`,
      { size: SZ.small, fill: C.ink2 }));
    const pw = D.p_wilcoxon.toExponential(0).split("e");
    S.halo(S.text(ga, (xa(17) + xa(36)) / 2, ya(D.null_median) + 9.5,
      `first in ${D.top1} of ${D.n} periods ($p$ = ${pw[0]}×10^{${pw[1].replace("-", "−")}})`, { anchor: "middle", size: SZ.small, fill: C.ink }));

    // x: every other period number
    const xt = ga.append("g").attr("transform", `translate(0,${A.h})`);
    P.forEach((p, i) => {
      xt.append("line").attr("x1", xa(p.goal)).attr("x2", xa(p.goal)).attr("y1", 0).attr("y2", i % 2 ? 1.2 : 2.2)
        .attr("stroke", C.ink2).attr("stroke-width", 0.5);
      if (i % 2 === 0) S.text(xt, xa(p.goal), 9.2, `${p.goal}`, { anchor: "middle", size: SZ.tick, fill: C.ink2 });
    });

    // key (below the axis)
    S.legend(g, A.x, A.y + A.h + 21, [
      { label: "named shared target", color: C.field, stroke: C.ink, sw: 0.45, size: 14 },
      { label: "free week, half-free #44, private #51", shape: d3.symbolSquare, fill: "#fff", stroke: C.ink2, sw: 0.8, size: 11 },
    ], { gap: 9 });

    // ------------------------------------------------------------------ (b) #51, weekly
    const B = { x: 30, y: 160, w: W - 30 - 4, h: 40 };
    S.panel(g, 0, B.y - 9, "b", "#51: each agent stays on its own private goal");
    const gb = g.append("g").attr("transform", `translate(${B.x},${B.y})`);
    const wk = D.weeks;
    const xb = d3.scalePoint().domain(wk.map((d) => d.week)).range([6, B.w - 6]);
    const yb = d3.scaleLinear().domain([0.42, 1.0]).range([B.h, 0]);
    S.axis(gb.append("g"), yb, "left", { ticks: [0.5, 0.75, 1], format: d3.format(".2f"), grid: true, length: B.w,
      title: "own goal wins", titleOffset: 21 });
    S.axis(gb.append("g").attr("transform", `translate(0,${B.h})`), xb, "bottom",
      { ticks: wk.map((d) => d.week), format: d3.format("d"), title: "week of #51", titleOffset: 10 });
    gb.append("line").attr("x1", 0).attr("x2", B.w).attr("y1", yb(0.5)).attr("y2", yb(0.5))
      .attr("stroke", C.muted).attr("stroke-width", 0.8).attr("stroke-dasharray", "3,2");
    S.halo(S.text(gb, B.w - 2, yb(0.5) - 2.5, "chance (swapped goal), 0.5", { anchor: "end", size: SZ.small, fill: C.ink2 }));
    gb.append("path").datum(wk).attr("d", d3.line().x((d) => xb(d.week)).y((d) => yb(d.acc)))
      .attr("fill", "none").attr("stroke", C.field).attr("stroke-width", 1.1);
    for (const w of wk) S.pointCI(gb, xb(w.week), yb(w.acc), yb(w.lo), yb(w.hi), { color: C.field, size: 12, stroke: C.ink, sw: 0.45 });
    S.halo(S.text(gb, 4, yb(0.72), `all weeks pooled: ${D.acc_all.toFixed(2)}`, { size: SZ.small, fill: FIELD_INK }));
  },
};
