// Fig. erasure (model 04, H15): work commits per call around a context erasure, forced (cap) vs voluntary.
// Data: data/processed/paper-figs/h15_erasure.json (export/h15_erasure.py; round-1b ledger, nine regime-III periods).
window.FIG = {
  width: 3.40, height: 2.12,
  draw(svg, D) {
    const { C } = S;
    const W = 3.40 * 72, H = 2.12 * 72;
    const m = { l: 30, r: 6, t: 15, b: 25 };
    const w = W - m.l - m.r, h = H - m.t - m.b;
    const g = svg.append("g");
    const p = g.append("g").attr("transform", `translate(${m.l},${m.t})`);
    const FORCED = C.vermillion, VOL = C.coupling;

    S.text(g, 0, 8.6, "Erasing the context window stalls the work", { size: S.SZ.title });

    const x = d3.scaleLinear().domain([-20.8, 20.8]).range([0, w]);
    const y = d3.scaleLinear().domain([0, 0.13]).range([h, 0]);

    // next-10-calls window (gray) and the erasure instant
    p.append("rect").attr("x", x(0.5)).attr("width", x(10.5) - x(0.5)).attr("y", 0).attr("height", h)
      .attr("fill", C.nullBand);
    S.text(p, (x(0.5) + x(10.5)) / 2, 7, "next 10 calls", { anchor: "middle", size: S.SZ.small, fill: C.ink2 });
    p.append("line").attr("x1", x(0)).attr("x2", x(0)).attr("y1", 0).attr("y2", h)
      .attr("stroke", C.ink2).attr("stroke-width", 0.6);
    S.text(p, x(0) - 2.2, h - 2.5, "erasure", { anchor: "start", rotate: -90, size: S.SZ.small, fill: C.ink2 });

    S.axis(p.append("g"), y, "left", { ticks: [0, 0.04, 0.08, 0.12], format: d3.format(".2f"),
      title: "work commits per call", titleOffset: 21 });
    S.axis(p.append("g").attr("transform", `translate(0,${h})`), x, "bottom",
      { ticks: [-20, -15, -10, -5, 0, 5, 10, 15, 20], format: (d) => (d > 0 ? "+" + d : d < 0 ? "−" + -d : "0"),
        title: "call relative to the erasure", titleOffset: 11.5 });

    // forced baseline: mean of calls −20…−11 (the reference of the dip), dashed across
    const cf = D.series.CF, cv = D.series.CV;
    const base = d3.mean(cf.filter((d) => d.off >= -20 && d.off <= -11), (d) => d.rate);
    p.append("line").attr("x1", x(-20)).attr("x2", x(20)).attr("y1", y(base)).attr("y2", y(base))
      .attr("stroke", FORCED).attr("stroke-width", 0.6).attr("stroke-dasharray", "2.2,1.6").attr("opacity", 0.75);

    const line = d3.line().x((d) => x(d.off)).y((d) => y(d.rate));
    for (const [s, col] of [[cv, VOL], [cf, FORCED]]) {
      for (const part of [s.filter((d) => d.off < 0), s.filter((d) => d.off > 0)]) {
        p.append("path").attr("d", line(part)).attr("fill", "none").attr("stroke", col).attr("stroke-width", 1.15)
          .attr("stroke-linejoin", "round");
      }
      for (const d of s) {
        p.append("circle").attr("cx", x(d.off)).attr("cy", y(d.rate)).attr("r", 1.45)
          .attr("fill", col).attr("stroke", "#fff").attr("stroke-width", 0.45);
      }
    }

    // direct labels
    S.halo(S.text(p, x(-15), y(0.0895), "voluntary", { anchor: "middle", size: S.SZ.label, fill: VOL }));
    S.halo(S.text(p, x(-15.5), y(0.0384) + 10.5, "forced (cap)", { anchor: "middle", size: S.SZ.label, fill: FORCED }));
    S.halo(S.text(p, x(15.5), y(base) - 3.2, "forced baseline", { anchor: "middle", size: S.SZ.small, fill: FORCED }));

    // the dip, as estimated per period and pooled (r1b_extra CTX_meta.CF_w)
    const pct = (v) => Math.round(100 * Math.abs(v));
    const dip = D.dip;
    const xm = (x(0.5) + x(10.5)) / 2;
    S.text(p, xm, 17.5, `forced −${pct(dip.mu)}%`, { anchor: "middle", size: S.SZ.label, fill: FORCED });
    S.text(p, xm, 25.5, `[−${pct(dip.lo)}, −${pct(dip.hi)}]`, { anchor: "middle", size: S.SZ.small, fill: FORCED });
    S.text(p, xm, 33, `${dip.below0}/${dip.k} periods`, { anchor: "middle", size: S.SZ.small, fill: C.ink2 });
  },
};
