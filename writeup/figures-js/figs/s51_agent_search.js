// Paper 2, Sec. results: the automatic search for individuals in goal period 51 (Fig. fig:search; card H148).
// a: each agent's own-state individuality (colonial A at 30 min) as a z-score against within-day permutations of its
//    own states, on the odd days and on the even days; one agent passes on both halves.
// b: local maxima of the boundary search on the real data and on rotated data, and how many held out of sample.
// Data: s51_agent_search.json (export/s51_agent_search.py).
window.FIG = {
  width: 3.40, height: 2.55,
  draw(svg, D) {
    const { C, SZ } = S;
    const W = 3.40 * 72, H = 2.55 * 72;
    const g = svg.append("g");
    const GOOD = "#0ca30c";

    // ------------------------------------------------------------------ a
    const A = { x: 22, y: 14, w: W - 22 - 3, h: 66 };
    S.panel(g, 0, 9, "a", "one agent predicts itself within the day");
    const ga = g.append("g").attr("transform", `translate(${A.x},${A.y})`);
    const n = D.agents.length;
    const x = d3.scalePoint().domain(d3.range(n)).range([4, A.w - 4]);
    const y = d3.scaleLinear().domain([-2.5, 5]).range([A.h, 0]);
    for (const a of D.agents) if (a.z_odd < -2.5 || a.z_even < -2.5 || a.z_odd > 5 || a.z_even > 5) throw new Error("z out of range " + a.name);
    S.axis(ga, y, "left", { ticks: [-2, 0, 2, 4], format: S.fmtMinus(d3.format("d")), grid: true, length: A.w, title: "$z$", titleOffset: 14 });
    ga.append("line").attr("x1", 0).attr("x2", A.w).attr("y1", y(D.z_thr)).attr("y2", y(D.z_thr)).attr("stroke", C.ink2)
      .attr("stroke-width", 0.5).attr("stroke-dasharray", "1.8,1.4");
    S.halo(S.text(ga, A.w - 1, y(D.z_thr) - 2, "$p$ = 0.025", { anchor: "end", size: SZ.small, fill: C.ink2 }), 2);
    for (const [i, a] of D.agents.entries()) {
      const col = a.individual ? GOOD : C.ink2;
      ga.append("line").attr("x1", x(i)).attr("x2", x(i)).attr("y1", y(a.z_odd)).attr("y2", y(a.z_even)).attr("stroke", col).attr("stroke-width", 0.5);
      ga.append("path").attr("d", S.sym(d3.symbolCircle, 8)).attr("transform", `translate(${x(i)},${y(a.z_odd)})`).attr("fill", col).attr("stroke", "#fff").attr("stroke-width", 0.5);
      ga.append("path").attr("d", S.sym(d3.symbolCircle, 8)).attr("transform", `translate(${x(i)},${y(a.z_even)})`).attr("fill", "#fff").attr("stroke", col).attr("stroke-width", 0.7);
      const t = S.text(ga, x(i), A.h + 3, a.name, { size: 5.8, fill: a.individual ? GOOD : C.ink2, anchor: "end", rotate: -60 });
    }
    S.legend(g, A.x + A.w - 78, A.y + 9, [{ label: "odd days", color: C.ink2, size: 8 }, { label: "even days", color: C.ink2, fill: "#fff", stroke: C.ink2, sw: 0.7, size: 8 }], { size: SZ.small });

    // ------------------------------------------------------------------ b
    const B = { x: 52, y: H - 36, w: W - 52 - 6, h: 26 };
    S.panel(g, 0, B.y - 9, "b", "the search finds as many maxima on rotated data");
    const gb = g.append("g").attr("transform", `translate(${B.x},${B.y})`);
    const xb = d3.scaleLinear().domain([0, 80]).range([0, B.w]);
    const rowsB = D.counts;
    const yb = d3.scaleBand().domain(rowsB.map((r) => r.level)).range([0, B.h]).paddingInner(0.35);
    S.axis(gb.append("g").attr("transform", `translate(0,${B.h})`), xb, "bottom", { ticks: [0, 20, 40, 60, 80], format: d3.format("d"), title: "local maxima", titleOffset: 8.5 });
    for (const r of rowsB) {
      const y0 = yb(r.level), bh = yb.bandwidth() / 2;
      gb.append("rect").attr("x", 0).attr("y", y0).attr("width", xb(r.real)).attr("height", bh - 0.4).attr("fill", C.ink2);
      gb.append("rect").attr("x", 0).attr("y", y0 + bh).attr("width", xb(r.rotated)).attr("height", bh - 0.4).attr("fill", "#c8c8c8");
      S.text(gb, -4, y0 + bh + 2.2, r.level, { anchor: "end", size: SZ.small, fill: C.ink });
      const inside = xb(r.rotated) > 100;   // long bars: label inside, white on dark
      S.text(gb, inside ? 3 : xb(r.real) + 2, y0 + bh - 1, `${r.real} real, ${r.real_held} held`, { size: 6.2, fill: inside ? "#fff" : C.ink2 });
      S.text(gb, inside ? 3 : xb(r.rotated) + 2, y0 + 2 * bh - 1, `${d3.format(".1f")(r.rotated)} rotated, ${d3.format(".1f")(r.rotated_held)} held`, { size: 6.2, fill: inside ? C.ink : C.ink2 });
    }
  },
};
