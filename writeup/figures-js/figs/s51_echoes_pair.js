// Paper 2, Sec. story: the Echoes pair. Daily commits of Gemini 2.5 Pro (author) and Claude Opus 4.8 (publisher)
// to the serial's two repositories, per working day of goal period 51, stacked. Top strip: the channel that carried
// chapters from Gemini to publication; dashed lines: channel switches; crosses: days Gemini lost a tool.
// Data: s51_echoes_pair.json (export/s51_echoes_pair.py).
window.FIG = {
  width: 3.40, height: 2.42,
  draw(svg, D) {
    const { C, F } = S;
    const W = 3.40 * 72, H = 2.42 * 72;
    const g = svg.append("g");

    // ------------------------------------------------------------------ x: working days, small gap per weekend
    const LM = 27, RM = 3, GAP = 1.2;
    const days = D.days, nD = days.length;
    const mon0 = d3.utcMonday(new Date(days[0] + "T00:00Z"));
    const week = days.map((d) => d3.utcMonday.count(mon0, new Date(d + "T00:00Z")));
    const dw = (W - LM - RM - week[nD - 1] * GAP) / nD;
    const xd = days.map((d, i) => LM + i * dw + week[i] * GAP);
    const di = new Map(days.map((d, i) => [d, i]));
    const xEnd = xd[nD - 1] + dw;

    // ------------------------------------------------------------------ y layout
    const sTop = 1, sH = 10.5;                   // channel strip
    const mY = sTop + sH + 6.2;                  // tool-loss row
    const pTop = mY + 6, pBot = H - 14;
    const y = d3.scaleLinear().domain([0, 700]).range([pBot, pTop]);
    if (D.checks.max_daily > 700) throw new Error("axis too short: " + D.checks.max_daily);

    // series, bottom to top
    const COL = {
      "29_echoes-of-the-real": "#D55E00", "29_echoes-inbox": "#f0b48a",
      "6_echoes-of-the-real": "#009E73", "6_echoes-inbox": "#9fd8c6",
    };
    const keys = Object.keys(COL);

    // grid
    for (const t of [200, 400, 600]) g.append("line").attr("x1", LM).attr("x2", xEnd).attr("y1", y(t)).attr("y2", y(t))
      .attr("stroke", C.grid).attr("stroke-width", 0.5);

    // channel-switch lines (under the bars)
    const chans = D.channels.map((c, i) => ({ ...c, a: xd[di.get(c.start)],
      b: i + 1 < D.channels.length ? xd[di.get(D.channels[i + 1].start)] - GAP * (week[di.get(D.channels[i + 1].start)] > week[di.get(D.channels[i + 1].start) - 1] ? 1 : 0) : xEnd }));
    for (const c of chans.slice(1)) g.append("line").attr("x1", c.a - 0.3).attr("x2", c.a - 0.3).attr("y1", sTop + sH).attr("y2", pBot)
      .attr("stroke", C.ink2).attr("stroke-width", 0.45).attr("stroke-dasharray", "1.5,1.2");

    // bars
    const gb = g.append("g");
    for (const r of D.rows) {
      let acc = 0;
      const x0 = xd[di.get(r.day)];
      for (const k of keys) {
        const v = r[k];
        if (!v) continue;
        gb.append("rect").attr("x", x0 + 0.35).attr("width", dw - 0.7).attr("y", y(acc + v)).attr("height", y(acc) - y(acc + v))
          .attr("fill", COL[k]);
        acc += v;
      }
    }

    // channel strip
    chans.forEach((c, i) => {
      const fill = c.short === "#focus" ? "#d2d2d2" : (i % 2 ? "#e2e2e2" : "#efefef");
      g.append("rect").attr("x", c.a).attr("y", sTop).attr("width", c.b - c.a - 0.6).attr("height", sH).attr("fill", fill);
      const lab = { "chat": "chat", "folder": "folder", "inbox repo": "inbox repo", "#focus": "#focus chat",
        "files": "files", "direct": "git" }[c.short];
      S.text(g, (c.a + c.b - 0.6) / 2, sTop + sH / 2 + 2.1, lab, { anchor: "middle", size: 5.9 });
    });

    // tool losses
    for (const t of D.tool_loss) {
      const xc = xd[di.get(t.day)] + dw / 2, s = 1.5;
      g.append("path").attr("d", `M${xc - s},${mY - s}L${xc + s},${mY + s}M${xc - s},${mY + s}L${xc + s},${mY - s}`)
        .attr("stroke", C.ink).attr("stroke-width", 0.7).attr("stroke-linecap", "round");
    }

    // axes
    S.axis(g.append("g").attr("transform", `translate(${LM - 1.5},0)`), y, "left",
      { ticks: [0, 200, 400, 600], format: d3.format("d"), title: "commits per day", titleOffset: 19 });
    const ax = g.append("g").attr("transform", `translate(0,${pBot + 0.4})`);
    ax.append("line").attr("x1", LM).attr("x2", xEnd).attr("stroke", C.ink2).attr("stroke-width", 0.5);
    let prevM = -1;
    days.forEach((d, i) => {
      const t = new Date(d + "T00:00Z");
      if (t.getUTCDay() !== 1 && i !== 0) return;
      ax.append("line").attr("x1", xd[i]).attr("x2", xd[i]).attr("y1", 0).attr("y2", 2.2).attr("stroke", C.ink2).attr("stroke-width", 0.5);
      const m = t.getUTCMonth();
      if (week[i] % 2 === 1 && m === prevM) return;              // label every other Monday, and each new month
      const s = m !== prevM ? d3.utcFormat("%b %-d")(t) : d3.utcFormat("%-d")(t);
      prevM = m;
      const tt = S.text(ax, xd[i], 8.6, s, { size: 6.6, fill: C.ink2, anchor: i === 0 ? "start" : "middle" });
      tt.selectAll("tspan").attr("font-family", F.tick);
    });

    // key, in the empty space above the #focus bars
    const kx = xd[di.get("2026-07-28")] + 1.5, ky = y(665);
    const items = [
      { k: "6_echoes-inbox", t: "Gemini, inbox repo" }, { k: "6_echoes-of-the-real", t: "Gemini, serial repo" },
      { k: "29_echoes-inbox", t: "Opus 4.8, inbox repo" }, { k: "29_echoes-of-the-real", t: "Opus 4.8, serial repo" },
    ];
    const kg = g.append("g"), card = kg.append("rect").attr("fill", "#fff");
    items.forEach((it, j) => {
      const yy = ky + j * 7.6;
      kg.append("rect").attr("x", kx).attr("y", yy - 4.3).attr("width", 7).attr("height", 5).attr("fill", COL[it.k]);
      S.text(kg, kx + 9.5, yy, it.t, { size: 6.2 });
    });
    const yy = ky + 4 * 7.6, xc = kx + 3.5, s = 1.5;
    kg.append("path").attr("d", `M${xc - s},${yy - 1.7 - s}L${xc + s},${yy - 1.7 + s}M${xc - s},${yy - 1.7 + s}L${xc + s},${yy - 1.7 - s}`)
      .attr("stroke", C.ink).attr("stroke-width", 0.7).attr("stroke-linecap", "round");
    S.text(kg, kx + 9.5, yy, "Gemini loses a tool", { size: 6.2 });
    const bb = kg.node().getBBox();
    card.attr("x", bb.x - 2).attr("y", bb.y - 1.5).attr("width", bb.width + 4).attr("height", bb.height + 3);
  },
};
