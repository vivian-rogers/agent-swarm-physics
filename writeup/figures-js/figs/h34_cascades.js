// Fig. cascades (model 03, H34): idea cascades are subcritical in every goal period.
// (a) cascade-size CCDF for #51 vs one branching law (GW-NB, 95% band) and the critical law; 31 other periods thin.
// (b) idea branching ratio per period vs room size, regimes I/II/III.
// Data: data/processed/paper-figs/h34_cascades.json (export/h34_cascades.py; round-1b, 32 non-reserved periods).
window.FIG = {
  width: 3.40, height: 4.30,
  draw(svg, D) {
    const { C, REG, REG_SHAPE } = S;
    const W = 3.40 * 72, H = 4.30 * 72;
    const g = svg.append("g");
    const Sm = D.summary;
    const f2 = d3.format(".2f");
    const RHAT = "$R@$";
    // put a circumflex over every italic "R@" tspan (the mini markup has no accents)
    const hats = (sel) => {
      sel.selectAll("tspan").filter(function () { return this.textContent === "R@"; }).each(function () {
        const t = d3.select(this).text("R");
        const fs = +t.attr("font-size"), rw = this.getComputedTextLength();
        const hat = d3.select(this.parentNode).insert("tspan", () => this.nextSibling).text("ˆ")
          .attr("font-family", S.F.body).attr("font-size", fs).attr("dy", -fs * 0.18);
        const hw = hat.node().getComputedTextLength();
        hat.attr("dx", -rw + (rw - hw) / 2 + fs * 0.1);
        const nx = hat.node().nextSibling;
        const after = d3.select(hat.node().parentNode).insert("tspan", () => nx).text("\u200b")
          .attr("font-size", fs).attr("dx", rw - hw - (rw - hw) / 2 - fs * 0.1).attr("dy", fs * 0.18);
      });
    };

    // ------------------------------------------------------------------ (a) CCDF
    const A = { l: 33, r: 6, t: 15, h: 135 };
    const aw = W - A.l - A.r;
    S.panel(g, 0, 8.6, "a", `Cascade sizes in #51 (${Sm.N51}-agent room)`);
    const pa = g.append("g").attr("transform", `translate(${A.l},${A.t})`);
    const xa = d3.scaleLog().domain([0.9, 32]).range([0, aw]);
    const ya = d3.scaleLog().domain([1.2e-5, 1.6]).range([A.h, 0]);
    const ycl = (v) => ya(Math.max(v, 1.2e-5));

    S.axis(pa.append("g"), ya, "left", { ticks: [1, 1e-1, 1e-2, 1e-3, 1e-4],
      format: (d) => (d === 1 ? "1" : `10^{−${Math.round(-Math.log10(d))}}`), title: "$P$($S$ ≥ $s$)", titleOffset: 24 });
    S.axis(pa.append("g").attr("transform", `translate(0,${A.h})`), xa, "bottom", { ticks: [1, 2, 5, 10, 20],
      format: d3.format("d"), title: "cascade size $s$ (agents in one exposure tree)", titleOffset: 11.5 });

    // 31 other periods
    const ln = d3.line().x((d) => xa(d[0])).y((d) => ya(d[1]));
    for (const o of D.others) {
      const pts = o.s.map((s, i) => [s, o.c[i]]).filter((d) => d[1] > 0);
      pa.append("path").attr("d", ln(pts)).attr("fill", "none").attr("stroke", C.sky).attr("stroke-width", 0.45)
        .attr("stroke-opacity", 0.55);
    }
    // one branching law (GW-NB at the fitted R, k): 95% band of 2000 simulated samples + the law itself
    const band = D.band;
    const area = d3.area().x((d) => xa(d.s)).y0((d) => ycl(d.lo > 0 ? d.lo : 1e-7)).y1((d) => ycl(d.hi));
    pa.append("path").attr("d", area(band)).attr("fill", C.null).attr("opacity", 0.55);
    pa.append("path").attr("d", ln(band.filter((d) => d.law > 1.2e-5).map((d) => [d.s, d.law])))
      .attr("fill", "none").attr("stroke", C.ink2).attr("stroke-width", 0.9).attr("stroke-dasharray", "3,1.8");
    // critical law: P(S >= s) = s^(-1/2)
    const crit = d3.range(1, 30.01, 0.5).map((s) => [s, Math.pow(s, -0.5)]);
    pa.append("path").attr("d", ln(crit)).attr("fill", "none").attr("stroke", C.ink).attr("stroke-width", 1.1)
      .attr("stroke-dasharray", "0.2,2.2").attr("stroke-linecap", "round");
    // #51 observed with Wilson 95% intervals
    for (const d of D.obs) {
      S.pointCI(pa, xa(d.s), ya(d.c), ycl(d.lo), ycl(d.hi), { color: C.coupling, size: 9, sw: 0.5 });
    }

    // direct labels
    const ang = (Math.atan2(ya(Math.pow(20, -0.5)) - ya(Math.pow(3, -0.5)), xa(20) - xa(3)) * 180) / Math.PI;
    const cx = xa(6.5), cy = ya(Math.pow(6.5, -0.5)) - 3.6;
    S.text(pa, cx, cy, "critical law $P$($s$) ∝ $s$^{−3/2}, $R$ = 1", { anchor: "middle", size: S.SZ.small, rotate: ang });
    S.halo(S.text(pa, xa(1.18), ya(2.2e-4), `#51: ${d3.format(",")(Sm.trees51)} trees`, { size: S.SZ.small, fill: C.coupling }));
    S.halo(S.text(pa, xa(1.18), ya(2.2e-4) + 8, `${RHAT} = ${f2(Sm.R51)}`, { size: S.SZ.small, fill: C.coupling }));
    S.text(pa, xa(8.6), ya(4.2e-5) - 7.6, "one branching law", { anchor: "end", size: S.SZ.small, fill: C.ink2 });
    S.text(pa, xa(8.6), ya(4.2e-5), `at ${RHAT}, 95% band`, { anchor: "end", size: S.SZ.small, fill: C.ink2 });
    S.text(pa, xa(9.5), ya(0.03), `${D.others.length} other periods`, { size: S.SZ.small, fill: "#3d8fc4" });

    // ------------------------------------------------------------------ (b) R-hat per period vs room size
    const B = { l: 33, r: 6, t: A.t + A.h + 46, h: 0 };
    B.h = H - B.t - 25;
    const bw = W - B.l - B.r;
    S.panel(g, 0, B.t - 6.4, "b", "Every period far below the critical point");
    const pb = g.append("g").attr("transform", `translate(${B.l},${B.t})`);
    const xb = d3.scaleLog().domain([3.4, 30]).range([0, bw]);
    const yb = d3.scaleLinear().domain([0, 1.12]).range([B.h, 0]);

    pb.append("rect").attr("x", 0).attr("width", bw).attr("y", yb(1.12)).attr("height", yb(1) - yb(1.12))
      .attr("fill", C.nullBand);
    S.axis(pb.append("g"), yb, "left", { ticks: [0, 0.2, 0.4, 0.6, 0.8, 1.0], format: d3.format(".1f"),
      title: `idea branching ratio ${RHAT}`, titleOffset: 24 });
    S.axis(pb.append("g").attr("transform", `translate(0,${B.h})`), xb, "bottom", { ticks: [4, 6, 10, 15, 25],
      format: d3.format("d"), title: "room size $N$ (agents)", titleOffset: 11.5 });
    pb.append("line").attr("x1", 0).attr("x2", bw).attr("y1", yb(1)).attr("y2", yb(1))
      .attr("stroke", C.ink2).attr("stroke-width", 0.9).attr("stroke-dasharray", "3,1.8");
    S.text(pb, 4, yb(1) - 2.6, "critical, $R$ = 1: ideas spread without limit", { size: S.SZ.small, fill: C.ink2 });

    const med = Sm.R_median;
    pb.append("line").attr("x1", 0).attr("x2", bw).attr("y1", yb(med)).attr("y2", yb(med))
      .attr("stroke", C.coupling).attr("stroke-width", 0.6).attr("stroke-dasharray", "1,1.6").attr("opacity", 0.9);
    S.halo(S.text(pb, bw - 1, yb(med) - 2.4, `median ${f2(med)}`, { anchor: "end", size: S.SZ.small, fill: C.coupling }));

    for (const rg of ["I", "II", "III"]) {
      for (const d of D.periods.filter((q) => q.regime === rg)) {
        S.pointCI(pb, xb(d.x), yb(d.R), yb(d.lo), yb(d.hi), { color: REG[rg], shape: REG_SHAPE[rg],
          size: rg === "II" ? 13 : 11, sw: 0.5 });
      }
    }

    S.text(pb, 4, yb(0.86), `${Sm.n_upper_below1}/${Sm.n_periods} periods: upper 95% bound below 1`, { size: S.SZ.small });
    S.text(pb, 4, yb(0.86) + 8, `${RHAT} from ${f2(Sm.R_min)} to ${f2(Sm.R_max)}`, { size: S.SZ.small });
    S.legend(pb, 4, yb(0.62), [
      { label: "regime I", color: REG.I, shape: REG_SHAPE.I, size: 12 },
      { label: "regime II", color: REG.II, shape: REG_SHAPE.II, size: 14 },
      { label: "regime III", color: REG.III, shape: REG_SHAPE.III, size: 12 },
    ], { gap: 8, size: S.SZ.small });
    hats(g);
  },
};
