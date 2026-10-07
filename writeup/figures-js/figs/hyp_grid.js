// Appendix: every hypothesis x every goal period / natural experiment, cell = verdict for that period.
// Rows grouped by primary physics model in the paper's order (useful, partly useful, the rest). Two pages:
// render "hyp_grid@1" and "hyp_grid@2". Data: hyp_grid.json (export/hyp_grid.py).
window.FIG = {
  width: 7.05, height: 9.05, data: "hyp_grid",
  draw(svg, D) {
    const { C } = S;
    const W = 7.05 * 72, H = 9.05 * 72;
    const part = +(window.VARIANT || 1);
    const ORDER = ["02", "09", "11", "01", "16", "17", "04", "03", "15", "14", "08", "05", "06", "07", "10", "12", "13", ""];
    const NAME = { ...D.names, "": "framework and method cards (no primary model)" };
    const TIER = (m) => (["02", "09", "11", "01", "16", "17"].includes(m) ? "useful"
      : ["04", "03", "15", "14", "08"].includes(m) ? "partly useful" : m === "" ? "" : "not useful");
    const VC = { supported: C.green, failed: C.up, mixed: "#9a9a9a", other: "#9a9a9a", descriptive: "#d4d4d4" };

    // ---- rows: group by primary model, split into two pages at a group boundary
    const groups = ORDER.map((m) => ({ m, rows: D.rows.filter((r) => (r.model || "") === m)
      .sort((a, b) => +a.id.slice(1) - +b.id.slice(1)) })).filter((g) => g.rows.length);
    const total = d3.sum(groups, (g) => g.rows.length);
    let acc = 0; const split = groups.findIndex((g) => (acc += g.rows.length) >= total / 2) + 1;
    const mine = part === 1 ? groups.slice(0, split) : groups.slice(split);

    // ---- columns
    const P = D.periods;
    const cellOf = new Map(D.cells.map((c) => [`${c.h}|${c.p}`, c]));
    const L = 156, R = 6, top = 138;
    const GAP = 7, colW = (W - L - R - GAP) / P.length;
    const nRows = d3.sum(mine, (g) => g.rows.length);
    const rowH = Math.min(7.0, (H - top - 6 - mine.length * 11) / nRows);
    const x = (i) => L + i * colW + (P[i] && P[i].kind === "NE" ? GAP : 0);
    const g = svg.append("g");

    // title line + legend
    S.text(g, 0, 8, part === 1 ? "Every hypothesis on every goal period it was tested on (part 1 of 2)" :
      "Every hypothesis on every goal period it was tested on (part 2 of 2)", { size: 8.2, bold: true });
    S.legend(g, 0, 21, [
      { label: "supported", rect: true, color: VC.supported },
      { label: "mixed or inconclusive", rect: true, color: VC.mixed },
      { label: "failed", rect: true, color: VC.failed },
      { label: "descriptive", rect: true, color: VC.descriptive },
      { label: "n/a or pending", color: C.muted, size: 4, stroke: "none" },
    ], { gap: 9, size: 6.4 });
    const lg2 = g.append("g").attr("transform", "translate(330,21)");
    lg2.append("rect").attr("x", 0).attr("y", -4.2).attr("width", 7).attr("height", 5.6).attr("fill", "#fff")
      .attr("stroke", C.ink).attr("stroke-width", 0.8);
    S.text(lg2, 9.5, 0.6, "confirmatory test", { size: 6.4 });
    lg2.append("rect").attr("x", 76).attr("y", -4.6).attr("width", 7).attr("height", 6.4).attr("fill", "#f3ece0");
    S.text(lg2, 85.5, 0.6, "reserved period", { size: 6.4 });

    // reserved-period shading and regime bands
    const gridTop = top, gridBot = top + nRows * rowH + mine.length * 11;
    P.forEach((p, i) => {
      if (p.reserved) g.append("rect").attr("x", x(i)).attr("y", gridTop - 3).attr("width", colW).attr("height", gridBot - gridTop + 3)
        .attr("fill", "#f3ece0");
    });
    const bands = d3.groups(P.map((p, i) => ({ ...p, i })), (p) => p.kind === "NE" ? "NE" : p.regime);
    for (const [k, ps] of bands) {
      const i0 = d3.min(ps, (p) => p.i), i1 = d3.max(ps, (p) => p.i) + 1;
      const col = k === "NE" ? C.ink2 : S.REG[k] || C.muted;
      g.append("rect").attr("x", x(i0) + 0.4).attr("y", top - 7).attr("width", x(i1 - 1) + colW - x(i0) - 0.8).attr("height", 2.2).attr("fill", col);
      if (k !== "NE") S.text(g, (x(i0) + x(i1 - 1) + colW) / 2, top - 22, `regime ${k}`,
        { anchor: "middle", size: 6.4, fill: col === C.ink2 ? C.ink2 : col });
    }
    const iNE = P.findIndex((p) => p.kind === "NE");
    const hdr = (a, b, label) => {
      S.text(g, (x(a) + x(b) + colW) / 2, top - 98, label, { anchor: "middle", size: 6.8, fill: C.ink });
      g.append("line").attr("x1", x(a) + 0.5).attr("x2", x(b) + colW - 0.5).attr("y1", top - 94.5).attr("y2", top - 94.5).attr("stroke", C.ink2).attr("stroke-width", 0.5);
    };
    hdr(0, iNE - 1, "goal periods (#)"); hdr(iNE, P.length - 1, "step changes in the setup (before vs. after)");
    // column labels (rotated)
    P.forEach((p, i) => {
      const lab = p.kind === "NE" ? p.label : p.id.replace(/^G0?/, "");
      const t = g.append("text").attr("x", 0).attr("y", 0).attr("transform", `translate(${x(i) + colW / 2 + 1.9},${top - 9}) rotate(-90)`)
        .attr("font-family", S.F.tick).attr("font-size", 5.6).attr("fill", C.ink2).text(lab);
    });

    // rows
    let y = top;
    for (const grp of mine) {
      y += 2;
      const tier = TIER(grp.m);
      S.text(g, 0, y + 6.5, `${grp.m ? grp.m + " " : ""}${NAME[grp.m]}`, { size: 6.8, bold: true });
      if (tier) S.text(g, W - R, y + 6.5, `${tier} · ${grp.rows.length} card${grp.rows.length > 1 ? "s" : ""}`,
        { size: 6, anchor: "end", fill: C.ink2 });
      g.append("line").attr("x1", 0).attr("x2", W - R).attr("y1", y + 8.5).attr("y2", y + 8.5).attr("stroke", C.rule).attr("stroke-width", 0.4);
      y += 9;
      for (const r of grp.rows) {
        const t = r.title.length > 40 ? r.title.slice(0, 39).replace(/[ ,:;-]+\S*$/, "") + "…" : r.title;
        const tt = g.append("text").attr("x", 0).attr("y", y + rowH * 0.78).attr("font-size", 5.9).attr("fill", C.ink);
        tt.append("tspan").attr("font-family", S.F.bold).text(r.id);
        // titles may carry x_y subscripts: draw them as subscripts, not literal underscores
        const parts = t.replace(/\\_/g, "_").split(/_\{?([A-Za-z0-9]+)\}?/);
        parts.forEach((seg, k) => {
          if (!seg) return;
          const ts = tt.append("tspan").attr("font-family", S.F.body).attr("fill", r.scored ? C.ink : C.muted).text(seg);
          if (k === 0) ts.attr("dx", 2.5);
          if (k % 2 === 1) ts.attr("font-size", 4.4).attr("dy", 1.2);
          else if (k > 0) ts.attr("dy", -1.2);
        });
        P.forEach((p, i) => {
          const c = cellOf.get(`${r.id}|${p.id}`);
          if (!c) return;
          if (c.v === "n/a" || c.v === "pending") {
            g.append("circle").attr("cx", x(i) + colW / 2).attr("cy", y + rowH / 2).attr("r", 0.7).attr("fill", C.muted);
            return;
          }
          g.append("rect").attr("x", x(i) + 0.45).attr("y", y + 0.5).attr("width", colW - 0.9).attr("height", rowH - 1.0)
            .attr("rx", 0.5).attr("fill", VC[c.v] || VC.mixed)
            .attr("stroke", c.confirm ? C.ink : "none").attr("stroke-width", c.confirm ? 0.8 : 0);
        });
        y += rowH;
      }
    }
  },
};
