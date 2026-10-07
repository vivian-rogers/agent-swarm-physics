// Sec. IV (model 02, H08): the response starts at the read-out call.
// (a) G38 offset profile of the excess chance that a call names the sender, own room vs other-room placebo;
// (b) the jump D = G(1) - G(0) per period for replies and mentions, with the other-room null.
// Data: data/processed/paper-figs/h08_readout_jump.json (export/h08_readout_jump.py). Units: percentage points.
window.FIG = {
  width: 3.40, height: 3.20,
  draw(svg, D) {
    const { C, SZ } = S;
    const W = 3.40 * 72;
    const g = svg.append("g");
    const INFL = "#5f5f5f";
    const fmt = (d) => S.fmtMinus(d3.format(d % 1 ? ".1f" : "d"))(d);

    // ------------------------------------------------------------------ (a) G38 offset profile
    const A = { x: 30, y: 24, w: W - 30 - 4, h: 66 };
    S.panel(g, 0, 8, "a", `${D.example}: the reader names the sender after reading`);
    const ga = g.append("g").attr("transform", `translate(${A.x},${A.y})`);
    const xa = d3.scaleLinear().domain([-2.5, 3.5]).range([0, A.w]);
    const ya = d3.scaleLinear().domain([-0.3, 1.6]).range([A.h, 0]);
    const colW = xa(0.5) - xa(-0.5);

    // the two calls that matter: in flight (o = 0) and read-out (o = 1)
    ga.append("rect").attr("x", xa(-0.5)).attr("y", -6).attr("width", colW).attr("height", A.h + 6)
      .attr("fill", "#000").attr("opacity", 0.055);
    ga.append("rect").attr("x", xa(0.5)).attr("y", -6).attr("width", colW).attr("height", A.h + 6)
      .attr("fill", C.coupling).attr("opacity", 0.09);
    S.text(ga, xa(0), -1.5, "in flight", { anchor: "middle", size: SZ.small, fill: INFL });
    S.text(ga, xa(1), -1.5, "read-out", { anchor: "middle", size: SZ.small, fill: C.coupling });

    S.axis(ga.append("g"), ya, "left", { ticks: [0, 0.5, 1, 1.5], format: fmt, title: "excess (pp)", titleOffset: 20 });
    S.axis(ga.append("g").attr("transform", `translate(0,${A.h})`), xa, "bottom",
      { ticks: [-2, -1, 0, 1, 2, 3], format: fmt, title: "reader’s call offset $o$", titleOffset: 10.5 });
    ga.append("line").attr("x1", 0).attr("x2", A.w).attr("y1", ya(0)).attr("y2", ya(0))
      .attr("stroke", C.ink2).attr("stroke-width", 0.5).attr("stroke-dasharray", "1.5,1.5");

    const own = D.profile.primary, oth = D.profile.other_room;
    // placebo: gray line, open squares
    ga.append("path").datum(oth).attr("d", d3.line().x((d) => xa(d.o)).y((d) => ya(d.G[0])))
      .attr("fill", "none").attr("stroke", C.muted).attr("stroke-width", 1.0);
    for (const d of oth) S.pointCI(ga, xa(d.o), ya(d.G[0]), ya(d.G[1]), ya(d.G[2]),
      { color: C.muted, fill: "#fff", stroke: C.muted, sw: 0.8, shape: d3.symbolSquare, size: 9 });
    // own room: blue band + line + points
    ga.append("path").datum(own).attr("d", d3.area().x((d) => xa(d.o)).y0((d) => ya(d.G[1])).y1((d) => ya(d.G[2])))
      .attr("fill", C.coupling).attr("opacity", 0.16);
    ga.append("path").datum(own).attr("d", d3.line().x((d) => xa(d.o)).y((d) => ya(d.G[0])))
      .attr("fill", "none").attr("stroke", C.coupling).attr("stroke-width", 1.3).attr("stroke-linejoin", "round");
    for (const d of own) S.pointCI(ga, xa(d.o), ya(d.G[0]), null, null, { color: C.coupling, size: 12 });

    // direct labels
    const o2 = own.find((d) => d.o === 2);
    S.halo(S.text(ga, xa(2) + 5, ya(o2.G[0]) - 4, "own room", { size: SZ.small, fill: C.coupling }));
    S.halo(S.text(ga, xa(-2.45), ya(0) + 8, "other-room placebo", { size: SZ.small, fill: C.ink2 }));
    // the jump D = G(1) - G(0), the quantity of panel (b)
    const g0 = own.find((d) => d.o === 0).G[0], g1 = own.find((d) => d.o === 1).G[0];
    const defs = svg.append("defs");
    defs.append("marker").attr("id", "h08arr").attr("viewBox", "0 0 6 6").attr("refX", 5.4).attr("refY", 3)
      .attr("markerWidth", 4).attr("markerHeight", 4).attr("orient", "auto")
      .append("path").attr("d", "M0,0.6L6,3L0,5.4z").attr("fill", C.ink);
    const xD = xa(1) + 7;
    ga.append("line").attr("x1", xa(0) + 3).attr("x2", xD + 2).attr("y1", ya(g0)).attr("y2", ya(g0))
      .attr("stroke", C.ink).attr("stroke-width", 0.5).attr("stroke-dasharray", "1.2,1.2");
    ga.append("line").attr("x1", xD).attr("x2", xD).attr("y1", ya(g0)).attr("y2", ya(g1) + 1)
      .attr("stroke", C.ink).attr("stroke-width", 0.6).attr("marker-end", "url(#h08arr)");
    S.halo(S.text(ga, xD + 2.5, ya((g0 + g1) / 2) + 2, "$D$", { size: SZ.label, fill: C.ink }));

    // ------------------------------------------------------------------ (b) jump per period
    const B = { x: 30, y: 136, w: W - 30 - 4, h: 70 };
    S.panel(g, 0, B.y - 12, "b", `The jump $D$ in all ${D.periods.length} periods`);
    const gb = g.append("g").attr("transform", `translate(${B.x},${B.y})`);
    const P = D.periods;
    const xb = d3.scaleBand().domain(P.map((d) => d.period)).range([0, B.w]).paddingInner(0).paddingOuter(0.02);
    const yb = d3.scaleLinear().domain([-0.5, 4]).range([B.h, 0]);
    const bw = xb.bandwidth();

    // regime tints behind the columns
    const REGS = [{ r: "I", lab: "regime I" }, { r: "II", lab: "II" }, { r: "II/III", lab: "II/III" }, { r: "III", lab: "regime III" }];
    const regCol = { I: C.green, II: C.pink, III: C.coupling, "II/III": C.muted };
    S.axis(gb.append("g"), yb, "left", { ticks: [0, 1, 2, 3, 4], format: fmt, title: "jump $D$ (pp)", titleOffset: 20,
      grid: true, length: B.w });
    gb.append("line").attr("x1", 0).attr("x2", B.w).attr("y1", yb(0)).attr("y2", yb(0))
      .attr("stroke", C.ink2).attr("stroke-width", 0.5);

    const off = { reply: -bw * 0.27, mention: bw * 0.02, null: bw * 0.3 };
    for (const d of P) {
      const cx = xb(d.period) + bw / 2;
      if (d.null) S.pointCI(gb, cx + off.null, yb(d.null[0]), yb(d.null[1]), yb(d.null[2]),
        { color: C.muted, fill: C.null, stroke: C.ink2, sw: 0.4, shape: d3.symbolSquare, size: 7 });
      S.pointCI(gb, cx + off.mention, yb(d.mention[0]), yb(d.mention[1]), yb(d.mention[2]),
        { color: C.coupling, fill: "#fff", stroke: C.coupling, sw: 0.75, size: 8, ciOpacity: 0.75 });
      S.pointCI(gb, cx + off.reply, yb(d.reply[0]), yb(d.reply[1]), yb(d.reply[2]), { color: C.coupling, size: 10 });
    }

    // x: period numbers, then regime brackets
    const xt = gb.append("g").attr("transform", `translate(0,${B.h})`);
    xt.append("line").attr("x1", 0).attr("x2", B.w).attr("stroke", C.ink2).attr("stroke-width", 0.5);
    for (const d of P) S.text(xt, xb(d.period) + bw / 2, 7.5, d.period.slice(1), { anchor: "middle", size: SZ.tick, fill: C.ink2 });
    for (const R of REGS) {
      const ps = P.filter((d) => d.regime === R.r);
      if (!ps.length) continue;
      const x0 = xb(ps[0].period) + 1.2, x1 = xb(ps[ps.length - 1].period) + bw - 1.2, yy = 11.5;
      xt.append("path").attr("d", `M${x0},${yy}V${yy + 2}H${x1}V${yy}`).attr("fill", "none")
        .attr("stroke", regCol[R.r]).attr("stroke-width", 0.8);
      S.text(xt, (x0 + x1) / 2, yy + 8.6, R.lab, { anchor: "middle", size: SZ.small, fill: regCol[R.r] });
    }

    // legend (top left, above the small regime-I jumps)
    S.legend(gb, 4, 6, [
      { label: "replies to the sender", color: C.coupling, size: 12 },
      { label: "names the sender", color: C.coupling, fill: "#fff", stroke: C.coupling, sw: 0.75, size: 10 },
      { label: "other room (null)", color: C.null, stroke: C.ink2, sw: 0.4, shape: d3.symbolSquare, size: 8 },
    ], { column: true, dy: 8.2 });
  },
};
