// Section II: the kickoff text is a field vector (H54, model 11). Genericness-corrected similarity of each period's
// day-1 content centroid (rows) to every candidate kickoff text (columns), 33 x 33, bge.
// Data: data/processed/paper-figs/s2_kickoff_matrix.json (export/s2_kickoff_matrix.py).
window.FIG = {
  width: 3.40, height: 2.86,
  draw(svg, D) {
    const { C, SZ } = S;
    const W = 3.40 * 72, H = 2.86 * 72;
    const g = svg.append("g");
    const n = D.n, M = D.S, v = D.vmax98;

    S.text(g, 0, 8, "Day 1 of each period lands on its own kickoff text", { size: SZ.title });

    const side = 166, mx = 34, my = 18;
    const cell = side / n;
    const gm = g.append("g").attr("transform", `translate(${mx},${my})`);

    // diverging scale, neutral white at 0: purple (less similar) - white - orange (more similar, the field color).
    // Values beyond the 98th percentile of |score| saturate (as in the H54 figure).
    // A mild power (1.5) keeps the many small scores pale, so the strong ones stand out; the color bar uses the same map.
    const col = (s) => { const u = Math.max(-1, Math.min(1, s / v)); return d3.interpolatePuOr(0.5 + 0.5 * Math.sign(u) * Math.abs(u) ** 1.5); };

    for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) {
      gm.append("rect").attr("x", j * cell).attr("y", i * cell).attr("width", cell + 0.02).attr("height", cell + 0.02)
        .attr("fill", col(M[i][j]));
    }
    // the diagonal: own kickoff, outlined
    for (let i = 0; i < n; i++) gm.append("rect").attr("x", i * cell + 0.2).attr("y", i * cell + 0.2)
      .attr("width", cell - 0.4).attr("height", cell - 0.4).attr("fill", "none").attr("stroke", C.ink).attr("stroke-width", 0.45);
    gm.append("rect").attr("width", side).attr("height", side).attr("fill", "none").attr("stroke", C.ink2).attr("stroke-width", 0.4);

    // ticks: selected period numbers at their row / column
    const lab = [3, 10, 20, 30, 40, 51];
    for (const gno of lab) {
      const k = D.goals.indexOf(gno), p = (k + 0.5) * cell;
      gm.append("line").attr("x1", p).attr("x2", p).attr("y1", side).attr("y2", side + 2).attr("stroke", C.ink2).attr("stroke-width", 0.5);
      gm.append("line").attr("y1", p).attr("y2", p).attr("x1", 0).attr("x2", -2).attr("stroke", C.ink2).attr("stroke-width", 0.5);
      S.text(gm, p, side + 9, `#${gno}`, { anchor: "middle", size: SZ.tick, fill: C.ink2 });
      S.text(gm, -3.6, p, `#${gno}`, { anchor: "end", baseline: "middle", size: SZ.tick, fill: C.ink2 });
    }
    S.text(gm, side / 2, side + 19.5, "candidate kickoff text", { anchor: "middle" });
    S.text(gm, -23, side / 2, "day-1 content of the period", { anchor: "middle", rotate: -90 });

    // color bar
    const cb = { x: mx + side + 12, y: my + 18, w: 5.5, h: side - 50 };
    const gc = g.append("g").attr("transform", `translate(${cb.x},${cb.y})`);
    const ys = d3.scaleLinear().domain([-v, v]).range([cb.h, 0]);
    const N = 60;
    for (let k = 0; k < N; k++) {
      const a = -v + (2 * v * k) / N, b = -v + (2 * v * (k + 1)) / N;
      gc.append("rect").attr("x", 0).attr("y", ys(b)).attr("width", cb.w).attr("height", ys(a) - ys(b) + 0.05).attr("fill", col((a + b) / 2));
    }
    gc.append("rect").attr("width", cb.w).attr("height", cb.h).attr("fill", "none").attr("stroke", C.ink2).attr("stroke-width", 0.4);
    const gax = gc.append("g").attr("transform", `translate(${cb.w},0)`);
    S.axis(gax, ys, "right", { ticks: [-0.4, -0.2, 0, 0.2, 0.4], format: (d) => (d === 0 ? "0" : d3.format(".1f")(d).replace("-", "−")), noLine: true });
    S.text(gc, cb.w / 2, -10.5, "more", { anchor: "middle", size: SZ.small, fill: C.ink2 });
    S.text(gc, cb.w / 2, -4, "alike", { anchor: "middle", size: SZ.small, fill: C.ink2 });
    S.text(gc, cb.w / 2, cb.h + 8, "less", { anchor: "middle", size: SZ.small, fill: C.ink2 });
    S.text(gc, cb.w / 2, cb.h + 14.5, "alike", { anchor: "middle", size: SZ.small, fill: C.ink2 });

    // legend for the outline: own kickoff
    const lx = cb.x - 4, ly = my + side + 9;
    g.append("rect").attr("x", lx).attr("y", ly - 4.4).attr("width", 5).attr("height", 5).attr("fill", col(v))
      .attr("stroke", C.ink).attr("stroke-width", 0.45);
    S.text(g, lx + 7.5, ly, "own", { size: SZ.small, fill: C.ink });
    S.text(g, lx + 7.5, ly + 7, "kickoff", { size: SZ.small, fill: C.ink });
  },
};
