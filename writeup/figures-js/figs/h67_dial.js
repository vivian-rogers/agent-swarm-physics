// Fig. dial (H67): read-out loop gain g against the equal-time talk dial g_eq, one point per goal period.
// The orange wedge between g = 0 and the diagonal is the part of equal-time co-talk that the read-out does not
// explain: the scheduler (a field) switching calls on together. Data: data/processed/paper-figs/h67_dial.json.
window.FIG = {
  width: 3.40, height: 2.55,
  draw(svg, D) {
    const { C, REG, REG_SHAPE } = S;
    const W = 3.40 * 72, H = 2.55 * 72;
    const m = { l: 31, r: 7, t: 15, b: 25 };
    const w = W - m.l - m.r, h = H - m.t - m.b;
    const g = svg.append("g");
    const p = g.append("g").attr("transform", `translate(${m.l},${m.t})`);
    const FIELD_INK = "#9a6500";

    S.text(g, 0, 8.6, "Talking at the same time is not reading each other", { size: S.SZ.title });

    const x = d3.scaleLinear().domain([-0.08, 0.44]).range([0, w]);
    const y = d3.scaleLinear().domain([Math.min(-0.12, d3.min(D.periods, (d) => d.lo) - 0.008), 0.38]).range([h, 0]);
    const [x0, x1] = x.domain(), [y0, y1] = y.domain();

    // the gap below the diagonal (0 <= g <= g_eq): co-talk the read-out does not explain
    const xe = Math.min(x1, y1);
    p.append("path").attr("d", `M${x(0)},${y(0)}L${x(x1)},${y(0)}L${x(x1)},${y(Math.min(x1, y1))}L${x(xe)},${y(xe)}Z`)
      .attr("fill", C.fieldSoft).attr("opacity", 0.75);

    // zero rules and the diagonal
    p.append("line").attr("x1", 0).attr("x2", w).attr("y1", y(0)).attr("y2", y(0)).attr("stroke", C.rule).attr("stroke-width", 0.5);
    p.append("line").attr("x1", x(0)).attr("x2", x(0)).attr("y1", 0).attr("y2", h).attr("stroke", C.rule).attr("stroke-width", 0.5);
    const d0 = Math.max(x0, y0), d1 = Math.min(x1, y1);
    p.append("line").attr("x1", x(d0)).attr("y1", y(d0)).attr("x2", x(d1)).attr("y2", y(d1))
      .attr("stroke", C.ink2).attr("stroke-width", 0.8).attr("stroke-dasharray", "3,1.8");
    const ang = (Math.atan2(y(0.3) - y(0.2), x(0.3) - x(0.2)) * 180) / Math.PI;
    S.halo(S.text(p, x(0.315) - 1.5, y(0.315) - 3, "read-out = equal-time", { anchor: "middle", rotate: ang, size: S.SZ.small, fill: C.ink2 }));

    S.axis(p.append("g"), y, "left", { ticks: [-0.1, 0, 0.1, 0.2, 0.3], format: S.fmtMinus(d3.format(".1f")),
      title: "read-out loop gain $g$", titleOffset: 22 });
    S.axis(p.append("g").attr("transform", `translate(0,${h})`), x, "bottom", { ticks: [0, 0.1, 0.2, 0.3, 0.4],
      format: S.fmtMinus(d3.format(".1f")), title: "equal-time talk dial $g$_{eq} (same calls)", titleOffset: 11.5 });

    // gap label (field ink), in the open part of the wedge
    S.text(p, x(0.435), y(0.215), "the gap: the scheduler", { anchor: "end", size: S.SZ.small, fill: FIELD_INK });
    S.text(p, x(0.435), y(0.215) + 7.4, "starts calls together", { anchor: "end", size: S.SZ.small, fill: FIELD_INK });

    // periods: regime I first (most numerous), then II, then III on top
    for (const rg of ["I", "II", "III"]) {
      for (const d of D.periods.filter((q) => q.regime === rg)) {
        S.pointCI(p, x(d.geq), y(d.g), y(d.lo), y(d.hi), { color: REG[rg], shape: REG_SHAPE[rg],
          size: rg === "II" ? 15 : rg === "I" ? 12 : 13, sw: 0.55, ciw: 0.65 });
      }
    }

    // legend (regimes are interleaved in II/I, so a key, not direct labels)
    S.legend(p, 3, 6, [
      { label: "regime I", color: REG.I, shape: REG_SHAPE.I, size: 13 },
      { label: "regime II", color: REG.II, shape: REG_SHAPE.II, size: 16 },
      { label: "regime III", color: REG.III, shape: REG_SHAPE.III, size: 14 },
    ], { column: true, dy: 8.6, size: S.SZ.small });
  },
};
