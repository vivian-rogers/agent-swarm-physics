// Sec. IV (model 02, H67): the read-out loop gain g per regime-III unit, and the part carried by reads that name the
// reader. Bar = g (one-kernel fit, the paper's number) with its 95% CI; dark = named part (two-kernel fit).
// Data: data/processed/paper-figs/h67_named.json (export/h67_named.py).
window.FIG = {
  width: 3.40, height: 2.19,
  draw(svg, D) {
    const { C, SZ } = S;
    const W = 3.40 * 72, H = 2.19 * 72;
    const g = svg.append("g");
    const U = D.units;
    const LIGHT = "#9fcbe8";

    S.text(g, 0, 8, "The gain is small; named reads carry about half of it", { size: SZ.title });

    const P = { x: 27, y: 41, w: W - 27 - 3, h: 82 };
    const gp = g.append("g").attr("transform", `translate(${P.x},${P.y})`);

    // x: units grouped by goal period, a small gap between periods
    const groups = d3.groups(U, (d) => d.goal);
    const gapG = 3.2, nU = U.length;
    const step = (P.w - gapG * (groups.length - 1)) / nU, bw = step * 0.66;
    let cx = 0;
    const pos = new Map();
    for (const [, us] of groups) { for (const u of us) { pos.set(u.unit, cx + step / 2); cx += step; } cx += gapG; }

    const y = d3.scaleLinear().domain([0, 0.42]).range([P.h, 0]);
    S.axis(gp.append("g"), y, "left", { ticks: [0, 0.1, 0.2, 0.3, 0.4], format: d3.format(".1f"), grid: true, length: P.w,
      title: "loop gain $g$", titleOffset: 19.5 });
    gp.append("line").attr("x1", 0).attr("x2", P.w).attr("y1", P.h).attr("y2", P.h).attr("stroke", C.ink2).attr("stroke-width", 0.5);

    // broken axis: the runaway line g = 1, drawn on a short strip above the plot
    const yTop = -20;
    gp.append("line").attr("x1", 0).attr("x2", 0).attr("y1", yTop - 4).attr("y2", yTop + 4).attr("stroke", C.ink2).attr("stroke-width", 0.5);
    gp.append("line").attr("x1", 0).attr("x2", -2.2).attr("y1", yTop).attr("y2", yTop).attr("stroke", C.ink2).attr("stroke-width", 0.5);
    S.text(gp, -3.8, yTop, "1.0", { anchor: "end", baseline: "middle", size: SZ.tick, fill: C.ink2 });
    for (const yy of [yTop + 6.5, -3.5]) {                 // the break marks
      gp.append("path").attr("d", `M-3,${yy + 1.4}L3,${yy - 1.4}`).attr("stroke", C.ink2).attr("stroke-width", 0.6);
    }
    gp.append("line").attr("x1", 0).attr("x2", 0).attr("y1", -3.5 + 0).attr("y2", 0).attr("stroke", C.ink2).attr("stroke-width", 0.5);
    gp.append("line").attr("x1", 0).attr("x2", P.w).attr("y1", yTop).attr("y2", yTop)
      .attr("stroke", C.ink).attr("stroke-width", 0.8).attr("stroke-dasharray", "3,2");
    S.halo(S.text(gp, P.w, yTop - 3, "$g$ = 1: each message causes one more, and echoes run away",
      { anchor: "end", size: SZ.small, fill: C.ink }));

    // bars: light = g, dark = named part; CI of g in ink
    for (const u of U) {
      const x0 = pos.get(u.unit) - bw / 2;
      if (u.g > 0) gp.append("rect").attr("x", x0).attr("width", bw).attr("y", y(u.g)).attr("height", y(0) - y(u.g)).attr("fill", LIGHT);
      if (u.named > 0) gp.append("rect").attr("x", x0).attr("width", bw).attr("y", y(u.named)).attr("height", y(0) - y(u.named))
        .attr("fill", C.coupling);
    }
    for (const u of U) {
      const xc = pos.get(u.unit);
      gp.append("line").attr("x1", xc).attr("x2", xc).attr("y1", y(Math.max(0, u.lo))).attr("y2", y(u.hi))
        .attr("stroke", C.ink).attr("stroke-width", 0.6).attr("stroke-linecap", "butt");
      gp.append("line").attr("x1", xc - bw / 2).attr("x2", xc + bw / 2).attr("y1", y(u.g)).attr("y2", y(u.g))
        .attr("stroke", C.ink).attr("stroke-width", 0.9);
    }

    // median line
    gp.append("line").attr("x1", 0).attr("x2", P.w).attr("y1", y(D.median)).attr("y2", y(D.median))
      .attr("stroke", C.ink2).attr("stroke-width", 0.6).attr("stroke-dasharray", "1,1.6");
    const xm = pos.get("38a") - step / 2;
    S.halo(S.text(gp, xm, y(D.median) - 2.5, `median ${D.median.toFixed(2)}`, { size: SZ.small, fill: C.ink2 }));

    // key (top left)
    S.legend(gp, 3, y(0.405), [
      { label: "reads that name the reader", color: C.coupling, rect: true },
      { label: "other reads", color: LIGHT, rect: true },
    ], { gap: 8 });
    const kg = gp.append("g").attr("transform", `translate(${3},${y(0.355)})`);
    kg.append("line").attr("x1", 3.5).attr("x2", 3.5).attr("y1", -5).attr("y2", 2.6).attr("stroke", C.ink).attr("stroke-width", 0.6);
    kg.append("line").attr("x1", 1.2).attr("x2", 5.8).attr("y1", -1.2).attr("y2", -1.2).attr("stroke", C.ink).attr("stroke-width", 0.9);
    S.text(kg, 9.5, 1.2, "$g$ with 95% CI", { size: SZ.small });

    // x labels: part letter under each bar, goal period under each group
    const xl = gp.append("g").attr("transform", `translate(0,${P.h})`);
    for (const [goal, us] of groups) {
      for (const u of us) {
        const part = u.unit.replace(/^\d+/, "");
        if (part) S.text(xl, pos.get(u.unit), 7, part, { anchor: "middle", size: 6.0, fill: C.muted });
      }
      const a = pos.get(us[0].unit) - bw / 2, b = pos.get(us[us.length - 1].unit) + bw / 2;
      const yy = us.length > 1 || us[0].unit.match(/[a-z]$/) ? 10.5 : 3.5;
      if (us.length > 1) xl.append("line").attr("x1", a).attr("x2", b).attr("y1", yy).attr("y2", yy)
        .attr("stroke", C.rule).attr("stroke-width", 0.5);
      S.text(xl, (a + b) / 2, yy + 7.5, `${goal}`, { anchor: "middle", size: SZ.tick, fill: C.ink2 });
    }
    S.text(xl, P.w / 2, 29, "goal period and its parts (regime III)", { anchor: "middle", size: SZ.label });
  },
};
