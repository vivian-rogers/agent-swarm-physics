// Section II: one real G38 message (star) and the model calls of its room-mates (H08, model 02).
// Data: data/processed/paper-figs/s2_readout_example.json (export/s2_readout_example.py).
window.FIG = {
  width: 3.40, height: 2.22,
  draw(svg, D) {
    const { C, F, SZ } = S;
    const W = 3.40 * 72, H = 2.22 * 72;
    const g = svg.append("g");
    const INFL = "#5f5f5f", CALL = "#d4d4d4";

    // colored run of text segments: [[str, color, italic?], ...]
    function runs(gg, x, y, segs, o = {}) {
      const t = gg.append("text").attr("x", x).attr("y", y).attr("text-anchor", o.anchor || "start")
        .attr("font-size", o.size || SZ.small);
      for (const [s, col, sz] of segs) {
        const ts = t.append("tspan").text(s).attr("fill", col || C.ink2).attr("font-family", F.body);
        if (sz) ts.attr("font-size", sz);
      }
      return S.halo(t, 2.6);
    }

    S.text(g, 0, 8, "A message acts at each reader's next call", { size: SZ.title });
    S.text(g, W - 1, 8, `${D.period}, ${D.day}`, { anchor: "end", size: SZ.small, fill: C.muted });

    const L = D.lanes;
    const rec = L.slice(1), grpA = rec.filter((r) => r.infl), grpB = rec.filter((r) => !r.infl);
    const P = { x: 60, w: W - 60 - 3, top: 20 };
    const x = d3.scaleLinear().domain([D.x0, D.x1]).range([P.x, P.x + P.w]);
    const laneH = 11.2, headH = 11.5, barH = 5.4;

    // vertical layout: sender, heading A, group A, heading B, group B
    const rows = [];
    let y = P.top + laneH / 2;
    rows.push({ lane: L[0], y }); y += laneH / 2;
    const hA = y + headH - 3.2; y += headH;
    for (const r of grpA) { y += laneH / 2; rows.push({ lane: r, y }); y += laneH / 2; }
    const hB = y + headH - 3.2; y += headH;
    for (const r of grpB) { y += laneH / 2; rows.push({ lane: r, y }); y += laneH / 2; }
    const yBot = y + 3;

    const clip = svg.append("defs").append("clipPath").attr("id", "ro-clip").append("rect")
      .attr("x", P.x).attr("y", 0).attr("width", P.w).attr("height", H);
    const gp = g.append("g").attr("clip-path", "url(#ro-clip)");

    // t = 0: the post
    // dashed, broken where the group headings run across it
    for (const [a, b] of [[P.top - 2, hA - 6.5], [hA + 2.5, hB - 6.5], [hB + 2.5, yBot]])
      g.append("line").attr("x1", x(0)).attr("x2", x(0)).attr("y1", a).attr("y2", b)
        .attr("stroke", C.muted).attr("stroke-width", 0.5).attr("stroke-dasharray", "2,1.6");

    // group headings
    runs(g, 0, hA, [["Call ", C.ink2], ["in flight", INFL], [" at the post: the message waits for the ", C.ink2],
      ["next call", C.coupling]]);
    runs(g, 0, hB, [["In a long pause: the ", C.ink2], ["next call", C.coupling], [" reads it and ", C.ink2], ["replies", C.coupling],
      [" (", C.ink2], ["▼", C.coupling, 4.6], [")", C.ink2]]);

    for (const { lane, y: yy } of rows) {
      // name
      S.text(g, P.x - 4, yy, lane.name, { anchor: "end", baseline: "middle", size: 6.5, fill: C.ink });
      // waiting line: from the post to the read-out call
      if (!lane.sender) gp.append("line").attr("x1", x(0)).attr("x2", x(lane.recv_s)).attr("y1", yy).attr("y2", yy)
        .attr("stroke", C.coupling).attr("stroke-width", 0.9).attr("stroke-dasharray", "0.9,1.5").attr("stroke-linecap", "round");
      for (const c of lane.calls) {
        const col = c.kind === "infl" ? INFL : c.kind === "recv" ? C.coupling : CALL;
        const x0 = x(c.s), x1 = x(Math.max(c.t, c.s + 1.2));
        gp.append("rect").attr("x", x0 + 0.35).attr("y", yy - barH / 2).attr("width", Math.max(0.8, x1 - x0 - 0.7))
          .attr("height", barH).attr("rx", 0.6).attr("fill", col);
      }
      const rc = lane.calls.find((c) => c.reply);
      if (rc) g.append("path").attr("d", d3.symbol().type(d3.symbolTriangle).size(15)())
        .attr("transform", `translate(${x(rc.t) + 0.5},${yy - barH / 2 - 2.4}) rotate(180)`)
        .attr("fill", C.coupling).attr("stroke", "#fff").attr("stroke-width", 0.5);
    }

    // the message: a star at t = 0 on the sender's lane, at the end of its posting call
    const ys = rows[0].y;
    g.append("path").attr("d", d3.symbol().type(d3.symbolStar).size(34)()).attr("transform", `translate(${x(0)},${ys})`)
      .attr("fill", C.coupling).attr("stroke", "#fff").attr("stroke-width", 0.6);
    S.halo(S.text(g, x(0) + 5, ys - 4.6, "the sender's message", { size: SZ.small, fill: C.ink }));


    // axis
    const ga = g.append("g").attr("transform", `translate(0,${yBot})`);
    S.axis(ga, x, "bottom", { ticks: [0, 50, 100, 150, 200], format: (d) => d, title: "time since the message (s)", titleOffset: 12 });
  },
};
