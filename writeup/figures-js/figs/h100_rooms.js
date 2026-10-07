// Rooms are spontaneous domains (H100). (a) cartoon: a room split with and without a room field, at three goals;
// (b) relabel excess Q_spont per regime-III period against random groupings; (c) cosine between consecutive periods'
// split directions against the joint-relabel null.
// Data: data/processed/paper-figs/h100_rooms.json (export/h100_rooms.py).
window.FIG = {
  width: 7.05, height: 2.26,
  draw(svg, D) {
    const { C } = S;
    const W = 7.05 * 72, H = 2.26 * 72;
    const g = svg.append("g");
    const defs = svg.append("defs");
    const mk = (id, col) => defs.append("marker").attr("id", id).attr("viewBox", "0 0 6 6").attr("refX", 5).attr("refY", 3)
      .attr("markerWidth", 4).attr("markerHeight", 4).attr("orient", "auto")
      .append("path").attr("d", "M0,0L6,3L0,6z").attr("fill", col);
    mk("arInk", C.ink); mk("arField", C.field);
    const REG3 = S.REG.III;
    const top = 24, bot = H - 29;                 // plot band shared by (b) and (c)

    // ------------------------------------------------------------------ (a) cartoon
    S.panel(g, 0, 9, "a", "Two ways a room split can form");
    const fs = 43, fg = 5, fx0 = 24, fy0 = 30, rg = 7;
    const BEST = { fill: C.ink2, stroke: "#fff" }, REST = { fill: "#fff", stroke: C.ink2 };
    for (let k = 0; k < 3; k++) S.text(g, fx0 + k * (fs + fg) + fs / 2, fy0 - 3.5, `goal ${k + 1}`,
      { anchor: "middle", size: 6.4, fill: C.ink2 });
    ["room field", "no field"].forEach((lab, r) => S.text(g, fx0 - 5, fy0 + r * (fs + rg) + fs / 2, lab,
      { anchor: "middle", rotate: -90, size: 6.6, fill: r === 0 ? "#9a6500" : C.ink2 }));
    const h = D.sim.h;
    for (const f of D.sim.frames) {
      const ox = fx0 + f.goal * (fs + fg), oy = fy0 + f.row * (fs + rg);
      const fr = g.append("g").attr("transform", `translate(${ox},${oy})`);
      fr.append("rect").attr("width", fs).attr("height", fs).attr("fill", "none").attr("stroke", "#dadada").attr("stroke-width", 0.5);
      const sx = d3.scaleLinear().domain([-1.5, 1.5]).range([0, fs]), sy = d3.scaleLinear().domain([-1.5, 1.5]).range([fs, 0]);
      if (f.row === 0) fr.append("line").attr("x1", sx(-1.25 * h[0])).attr("y1", sy(-1.25 * h[1] - 0.95))
        .attr("x2", sx(1.25 * h[0])).attr("y2", sy(1.25 * h[1] - 0.95))
        .attr("stroke", C.field).attr("stroke-width", 1.1).attr("marker-end", "url(#arField)");
      for (const [pts, st, shp] of [[f.rest, REST, d3.symbolSquare], [f.best, BEST, d3.symbolCircle]])
        for (const p of pts) fr.append("path").attr("d", S.sym(shp, shp === d3.symbolSquare ? 4.2 : 5.2))
          .attr("transform", `translate(${sx(p[0])},${sy(p[1])})`).attr("fill", st.fill).attr("stroke", st.stroke)
          .attr("stroke-width", 0.45);
      fr.append("line").attr("x1", sx(-0.5 * f.d[0])).attr("y1", sy(-0.5 * f.d[1]))
        .attr("x2", sx(0.5 * f.d[0])).attr("y2", sy(0.5 * f.d[1]))
        .attr("stroke", C.ink).attr("stroke-width", 0.9).attr("marker-end", "url(#arInk)");
    }
    S.legend(g, fx0 - 2, fy0 + 2 * fs + rg + 11, [
      { label: "room A", color: C.ink2, size: 7 },
      { label: "room B", fill: "#fff", stroke: C.ink2, sw: 0.5, shape: d3.symbolSquare, size: 6 },
    ], { gap: 6, size: 6.2 });
    S.legend(g, fx0 - 2, fy0 + 2 * fs + rg + 20, [
      { label: "split", line: true, color: C.ink, width: 0.9 },
      { label: "field $h$", line: true, color: C.field, width: 1.1 },
    ], { gap: 6, size: 6.2 });

    // ------------------------------------------------------------------ (b) relabel excess per period
    const Bx = 192, Bw = 140;
    S.panel(g, Bx - 26, 9, "b", "Rooms differ beyond random groupings");
    const gb = g.append("g").attr("transform", `translate(${Bx},0)`);
    const per = D.periods;
    const xb = d3.scaleBand().domain(per.map((d) => d.period)).range([0, Bw]).paddingInner(0.3).paddingOuter(0.15);
    const yb = d3.scaleLinear().domain([0, 6.2]).range([bot, top]);
    S.axis(gb.append("g"), yb, "left", { ticks: [0, 2, 4, 6], title: "relabel excess $Q$_{spont}", titleOffset: 12 });
    const axb = gb.append("g").attr("transform", `translate(0,${bot})`);
    S.axis(axb, xb, "bottom", { ticks: per.map((d) => d.period), format: (d) => `#${d}`, noTicks: true, title: "goal period", titleOffset: 12 });
    for (const d of per) {
      const x = xb(d.period), bw = xb.bandwidth();
      gb.append("rect").attr("x", x).attr("width", bw).attr("y", yb(d.null95)).attr("height", yb(0) - yb(d.null95))
        .attr("fill", C.nullBand);
      const sig = d.p < 0.05;
      gb.append("circle").attr("cx", x + bw / 2).attr("cy", yb(d.Q)).attr("r", 2.3)
        .attr("fill", sig ? REG3 : "#fff").attr("stroke", sig ? "#fff" : REG3).attr("stroke-width", sig ? 0.6 : 0.8);
    }
    const nsig = per.filter((d) => d.p < 0.05).length;
    const ty = yb(4.75);
    S.text(gb, 3, ty, `${nsig} of ${per.length} above random`, { size: 6.6, fill: REG3 });
    S.text(gb, 3, ty + 8, "gray: 95th percentile of", { size: 6.2, fill: C.muted });
    S.text(gb, 3, ty + 15, "random groupings", { size: 6.2, fill: C.muted });
    for (const d of per.filter((d) => d.p >= 0.05))
      S.text(gb, xb(d.period) + xb.bandwidth() / 2, yb(Math.max(d.null95, d.Q)) - 4.5, "n.s.", { anchor: "middle", size: 6.0, fill: C.muted });

    // ------------------------------------------------------------------ (c) persistence of the split direction
    const Cx = 374, Cw = W - Cx - 2;
    S.panel(g, Cx - 30, 9, "c", "The split direction resets at each goal");
    const gc = g.append("g").attr("transform", `translate(${Cx},0)`);
    const rem = D.remanence;
    const xc = d3.scaleBand().domain(rem.map((d) => d.P1)).range([0, Cw]).paddingInner(0.32).paddingOuter(0.12);
    const yc = d3.scaleLinear().domain([-1, 1]).range([bot, top]);
    S.axis(gc.append("g"), yc, "left", { ticks: [-1, -0.5, 0, 0.5, 1], format: (d) => d === 0 ? "0" : d3.format("+.1~f")(d).replace("-", "−"),
      title: "cosine of split directions, $R$", titleOffset: 20 });
    gc.append("line").attr("x1", 0).attr("x2", Cw).attr("y1", yc(0)).attr("y2", yc(0))
      .attr("stroke", C.rule).attr("stroke-width", 0.5).attr("stroke-dasharray", "1.5,1.5");
    const axc = gc.append("g").attr("transform", `translate(0,${bot})`);
    S.axis(axc, xc, "bottom", { ticks: rem.map((d) => d.P1), format: (d) => "", noTicks: true, noLine: false,
      title: "consecutive goal periods", titleOffset: 12 });
    for (const d of rem) {
      const x = xc(d.P1), bw = xc.bandwidth(), cx = x + bw / 2;
      S.text(axc, cx, 3.8, `${d.P1}–${d.P2}`, { anchor: "middle", baseline: "hanging", size: 6.4, fill: C.ink2 });
      gc.append("rect").attr("x", x).attr("width", bw).attr("y", yc(d.hi)).attr("height", yc(d.lo) - yc(d.hi))
        .attr("fill", C.nullBand);
      gc.append("line").attr("x1", x).attr("x2", x + bw).attr("y1", yc(d.mean)).attr("y2", yc(d.mean))
        .attr("stroke", C.null).attr("stroke-width", 0.8);
      gc.append("circle").attr("cx", cx).attr("cy", yc(d.R)).attr("r", 2.3).attr("fill", REG3).attr("stroke", "#fff").attr("stroke-width", 0.6);
    }
    const m = rem.find((d) => d.merge);
    const mx = xc(m.P1) + xc.bandwidth() / 2;
    gc.append("line").attr("x1", mx).attr("x2", mx).attr("y1", yc(m.lo) + 2).attr("y2", yc(-0.62))
      .attr("stroke", C.muted).attr("stroke-width", 0.5);
    S.halo(S.text(gc, mx, yc(-0.62) + 7, "rooms merged", { anchor: "middle", size: 6.2, fill: C.ink2 }));
    S.halo(S.text(gc, mx, yc(-0.62) + 14, "in between", { anchor: "middle", size: 6.2, fill: C.ink2 }));
    S.text(gc, Cw - 1, yc(0.97), "gray: random groupings", { anchor: "end", size: 6.2, fill: C.muted });
  },
};
