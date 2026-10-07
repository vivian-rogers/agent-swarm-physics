// Model 17: collective modes against a calibrated random-matrix edge (H12 round 1b). Single column.
// (a) top eigenvalue / 95% surrogate edge per unit, three channels; (b) #12 debates, participation ratio, paired.
// Data: data/processed/paper-figs/m17_modes.json (export/m17_modes.py).
window.FIG = {
  width: 3.40, height: 3.23,
  draw(svg, D) {
    const { C, SZ } = S;
    const W = 3.40 * 72, H = 3.23 * 72;
    const g = svg.append("g");

    // deterministic beeswarm: place points in order of y; each takes the nearest free x offset
    function swarm(ys, r) {
      const order = ys.map((y, i) => [y, i]).sort((a, b) => a[0] - b[0]);
      const placed = [], xs = new Array(ys.length);
      for (const [y, i] of order) {
        for (let k = 0; k < 200; k++) {
          const dx = (k % 2 ? 1 : -1) * Math.ceil(k / 2) * 0.6;
          if (placed.every((p) => (p.x - dx) ** 2 + (p.y - y) ** 2 >= (2 * r + 0.35) ** 2)) {
            xs[i] = dx; placed.push({ x: dx, y }); break;
          }
        }
      }
      return xs;
    }

    // ------------------------------------------------------------------ (a)
    const A = { x: 30, y: 17, w: W - 30 - 3, h: 96 };
    S.panel(g, 0, 8, "a", "A real mode in talk and content; activity sits at the edge");
    const ga = g.append("g").attr("transform", `translate(${A.x},${A.y})`);
    const y = d3.scaleLog().domain([0.86, 2.75]).range([A.h, 0]);
    const xb = d3.scaleBand().domain(D.channels.map((c) => c.name)).range([0, A.w]).paddingInner(0.12).paddingOuter(0.06);
    ga.append("rect").attr("x", 0).attr("width", A.w).attr("y", y(1)).attr("height", A.h - y(1)).attr("fill", C.nullBand);
    S.axis(ga, y, "left", { ticks: [1, 1.5, 2, 2.5], format: (d) => String(d), grid: true, length: A.w,
      title: "top eigenvalue / noise edge", titleOffset: 20 });
    ga.append("line").attr("x1", 0).attr("x2", A.w).attr("y1", y(1)).attr("y2", y(1)).attr("stroke", C.ink2).attr("stroke-width", 0.7);
    S.text(ga, A.w - 2, A.h - 2.5, "noise (95% edge)", { anchor: "end", size: SZ.small, fill: C.ink2 });

    const sub = { activity: ["activity", "block-shift null"], talk: ["talk", "block-shift null"],
      content: ["content (bge)", "cross-day null"] };
    const R = 1.8;
    for (const c of D.channels) {
      const cx = xb(c.name) + xb.bandwidth() / 2;
      const py = c.y.map((v) => y(v));
      const dx = swarm(py, R);
      const med = d3.median(c.y);
      c.y.forEach((v, i) => {
        const up = v > 1;
        ga.append("circle").attr("cx", cx + dx[i]).attr("cy", py[i]).attr("r", R)
          .attr("fill", up ? C.coupling : "#fff").attr("stroke", up ? "#fff" : C.muted).attr("stroke-width", up ? 0.45 : 0.7);
      });
      // median bar, over the points
      ga.append("line").attr("x1", cx - 15).attr("x2", cx + 15).attr("y1", y(med)).attr("y2", y(med))
        .attr("stroke", C.ink).attr("stroke-width", 1.1).attr("stroke-linecap", "round");
      const ytop = Math.min(...py) - R - 3.5;
      S.text(ga, cx, Math.max(6, ytop), `${c.above}/${c.n} above`, { anchor: "middle", size: SZ.small, fill: C.ink });
      S.text(ga, cx, A.h + 9.5, sub[c.name][0], { anchor: "middle", size: SZ.label, fill: C.ink, baseline: "middle" });
      S.text(ga, cx, A.h + 17.5, sub[c.name][1], { anchor: "middle", size: SZ.small, fill: C.ink2, baseline: "middle" });
      if (c.name === "content") S.text(ga, cx - 18, y(med), `median ${c.median.toFixed(2)}`,
        { anchor: "end", size: SZ.small, fill: C.ink, baseline: "middle" });
    }

    // ------------------------------------------------------------------ (b)
    const top2 = A.y + A.h + 34;
    const P = D.debates.pairs.slice().sort((a, b) => b.off - a.off);
    const rowH = 5.6;
    const B = { x: 30, y: top2 + 11, w: W - 30 - 3, h: P.length * rowH };
    S.panel(g, 0, top2, "b", "#12 debates: content narrows while a motion is on");
    const gb = g.append("g").attr("transform", `translate(${B.x},${B.y})`);
    const x = d3.scaleLinear().domain([3.4, 13.6]).range([0, B.w]);
    S.axis(gb.append("g").attr("transform", `translate(0,${B.h + 2})`), x, "bottom",
      { ticks: [6, 8, 10, 12], format: (d) => d, grid: false, title: "participation ratio of content (bge)", titleOffset: 10.5 });
    for (const t of [6, 8, 10, 12]) gb.append("line").attr("x1", x(t)).attr("x2", x(t)).attr("y1", -2).attr("y2", B.h + 2)
      .attr("stroke", C.grid).attr("stroke-width", 0.5);
    P.forEach((p, i) => {
      const yy = (i + 0.5) * rowH;
      gb.append("line").attr("x1", x(p.off)).attr("x2", x(p.on)).attr("y1", yy).attr("y2", yy)
        .attr("stroke", p.on < p.off ? C.field : C.muted).attr("stroke-width", 0.9).attr("opacity", 0.55);
      gb.append("circle").attr("cx", x(p.off)).attr("cy", yy).attr("r", 1.9).attr("fill", "#fff")
        .attr("stroke", C.ink2).attr("stroke-width", 0.7);
      gb.append("circle").attr("cx", x(p.on)).attr("cy", yy).attr("r", 2.0).attr("fill", C.field)
        .attr("stroke", "#fff").attr("stroke-width", 0.45);
    });
    // direct labels on the top row
    const p0 = P[0];
    S.text(gb, x(p0.off) + 2.2, -3.5, "after the verdict", { anchor: "end", size: SZ.small, fill: C.ink2 });
    S.text(gb, x(p0.on), -3.5, "motion on", { anchor: "middle", size: SZ.small, fill: "#a86f00" });
    const d = D.debates;
    const rel = Math.round(d.median_rel * 100);
    S.text(gb, 0, 5, `lower in ${d.n_low}/${d.n}`, { size: SZ.small, fill: C.ink });
    S.text(gb, 0, 12.5, `median ${rel < 0 ? "−" : "+"}${Math.abs(rel)}%`, { size: SZ.small, fill: C.ink });
    S.text(gb, 0, 20, `$p$ = ${d.p.toFixed(3)}`, { size: SZ.small, fill: C.ink });
  },
};
