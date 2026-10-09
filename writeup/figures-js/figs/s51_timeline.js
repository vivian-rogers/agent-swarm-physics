// Paper 2, Sec. story: goal period 51 (07-06 -> 09-04, working days only) as a swimlane.
// Top: the four phases of the story section. Below: event lines with labels. Lanes: one per agent, by join date;
// each working day is colored by the agent's dominant project that day (modal touched project of its non-pause calls).
// Black outline: the two #focus residents' time in that room. Data: s51_timeline.json (export/s51_timeline.py).
window.FIG = {
  width: 7.05, height: 4.2,
  draw(svg, D) {
    const { C, F } = S;
    const W = 7.05 * 72, H = 4.2 * 72;
    const g = svg.append("g");

    // ------------------------------------------------------------------ colors (ten named projects + three grays)
    const COL = {
      echoes: "#882255", welfare: "#117733", frame: "#CC6677", gates: "#AA4499", keystone: "#E69F00",
      disproof: "#332288", news: "#88CCEE", hub: "#44AA99", merch: "#DDCC77", compass: "#999933",
      own: "#a3a3a3", other: "#cfcfcf", none: "#ececec",
    };
    const INK = { echoes: "#fff", disproof: "#fff", welfare: "#fff", gates: "#fff" };

    // ------------------------------------------------------------------ x: working days with a small gap per weekend
    const LM = 57, RM = 3, GAP = 1.8;
    const days = D.days, nD = days.length;
    const week = days.map((d, i) => d3.utcMonday.count(d3.utcMonday(new Date(days[0] + "T00:00Z")), new Date(d + "T00:00Z")));
    const nW = week[nD - 1];
    const dw = (W - LM - RM - nW * GAP) / nD;
    const xd = days.map((d, i) => LM + i * dw + week[i] * GAP);
    const di = new Map(days.map((d, i) => [d, i]));
    const X = (day, h = 0) => xd[di.get(day)] + (h / D.day_hours) * dw;
    const xEnd = xd[nD - 1] + dw;
    // UTC time -> x (time outside the 8-h day snaps to the day's edge; weekend time snaps to Monday 09:00)
    const H0 = D.day_start_utc, fmt = d3.utcFormat("%Y-%m-%d");
    function Xt(iso) {
      const t = new Date(iso);
      let a = new Date(t.getTime() - H0 * 3600e3);              // the PT working day this time belongs to
      let d = fmt(a), h = (t.getTime() - (Date.parse(d + "T00:00Z") + H0 * 3600e3)) / 3600e3;
      if (!di.has(d)) {                                         // weekend: next Monday morning
        while (!di.has(d) && d <= days[nD - 1]) { a = new Date(a.getTime() + 86400e3); d = fmt(a); h = 0; }
        if (!di.has(d)) return xEnd;
      }
      return X(d, Math.max(0, Math.min(D.day_hours, h)));
    }

    // ------------------------------------------------------------------ y layout
    const pTop = 1, pH = 16;                                   // phase strip
    const eRows = [pTop + pH + 7.4, pTop + pH + 14.6, pTop + pH + 21.8];
    const lTop = eRows[2] + 4.6, pitch = 6.55, barH = 5.0, nGap = 3.2;
    const agents = D.agents;
    agents.forEach((a, i) => { a.y = lTop + i * pitch + (a.newcomer ? nGap : 0); });
    const lBot = agents[agents.length - 1].y + pitch;
    const axY = lBot + 1.2;

    // ------------------------------------------------------------------ NE33 band and event lines (under the lanes)
    const gl = g.append("g");
    const ev = Object.fromEntries(D.events.map((e) => [e.key, e]));
    const n33 = ev.ne33;
    gl.append("rect").attr("x", X(n33.day)).attr("y", eRows[0] + 2).attr("width", X(n33.end) + dw - X(n33.day))
      .attr("height", lBot - eRows[0] - 2).attr("fill", "#f3f3f3");
    const lineTo = { ne38: 0, aug05: 0, nudge: 2, aug24: 1 };
    for (const e of D.events.filter((e) => e.key !== "ne33")) {
      const xe = X(e.day, e.h);
      gl.append("line").attr("x1", xe).attr("x2", xe).attr("y1", eRows[lineTo[e.key]] + 1.6).attr("y2", lBot)
        .attr("stroke", C.ink2).attr("stroke-width", 0.5).attr("stroke-dasharray", "1.6,1.3");
      e.x = xe;
    }

    // ------------------------------------------------------------------ phase strip
    for (const [i, P] of D.phases.entries()) {
      const a = X(P.start), b = X(P.end) + dw;
      g.append("rect").attr("x", a + (i ? 0.6 : 0)).attr("y", pTop).attr("width", b - a - (i ? 0.6 : 0)).attr("height", pH)
        .attr("fill", i % 2 ? "#dedede" : "#ebebeb");
      const lines = { 0: ["Roles, a coordinator", "and solo artifacts"], 1: ["A reassignment", "and a ritual"],
        2: ["A quiet room; the operator", "steps back"], 3: ["Service loops", "and newcomers"] }[i];
      S.text(g, (a + b) / 2, pTop + 6.6, lines[0], { anchor: "middle", size: 6.2 });
      S.text(g, (a + b) / 2, pTop + 13.4, lines[1], { anchor: "middle", size: 6.2 });
    }
    S.text(g, LM - 3, pTop + 10.2, "phase", { anchor: "end", size: 6.2, fill: C.ink2 });

    // ------------------------------------------------------------------ event labels
    const lab = (x, row, str, anchor) => S.halo(S.text(g, x, eRows[row], str, { anchor, size: 6.2, fill: C.ink }), 2.4);
    lab(ev.ne38.x - 1.5, 0, "Opus 5 made mathematician (NE38)", "end");
    lab(ev.aug05.x + 1.5, 0, "pause–resume ends; #focus opens;", "start");
    lab(ev.aug05.x + 1.5, 1, "operator rebukes DeepSeek-V3.2", "start");
    lab(ev.nudge.x - 1.5, 2, "nudger off", "end");
    lab(ev.aug24.x + 1.5, 1, "outreach veto; #focus closes", "start");
    S.text(g, (X(n33.day) + X(n33.end) + dw) / 2, eRows[2], "NE33", { anchor: "middle", size: 6.2, fill: C.ink });
    S.text(g, LM - 3, eRows[1], "events", { anchor: "end", size: 6.2, fill: C.ink2 });

    // ------------------------------------------------------------------ lanes
    const gm = g.append("g");
    const byA = d3.group(D.cells, (c) => c.agent);
    for (const a of agents) {
      const y0 = a.y + (pitch - barH) / 2;
      const xa = X(a.joined in Object.fromEntries(days.map((d) => [d, 1])) ? a.joined : days[0]);
      gm.append("line").attr("x1", xa).attr("x2", xEnd).attr("y1", y0 + barH / 2).attr("y2", y0 + barH / 2)
        .attr("stroke", "#d6d6d6").attr("stroke-width", 0.35);
      for (const c of byA.get(a.agent) || []) {
        const i = di.get(c.day);
        const contig = i + 1 < nD && week[i + 1] === week[i];
        gm.append("rect").attr("x", xd[i]).attr("y", y0).attr("width", dw + (contig ? 0.25 : 0)).attr("height", barH)
          .attr("fill", COL[c.cat]);
      }
      const t = S.text(g, LM - 3, a.y + pitch / 2 + 2.1, a.name, { anchor: "end", size: 6.0, fill: C.ink });
      if (a.newcomer) {
        const xj = X(a.joined);
        gm.append("path").attr("d", `M${xj - 3.2},${y0 - 0.1}L${xj - 0.4},${y0 + barH / 2}L${xj - 3.2},${y0 + barH + 0.1}Z`)
          .attr("fill", C.ink);
      }
    }
    // newcomer divider label
    const firstNew = agents.find((a) => a.newcomer);
    g.append("line").attr("x1", 4).attr("x2", LM - 3).attr("y1", firstNew.y - nGap / 2 + 0.2).attr("y2", firstNew.y - nGap / 2 + 0.2)
      .attr("stroke", C.rule).attr("stroke-width", 0.4);

    // ------------------------------------------------------------------ #focus residence (outline on the two lanes)
    const gf = g.append("g");
    for (const A of [6, 29]) {
      const a = agents.find((r) => r.agent === A);
      // residence: first entry on 08-05 to the exit on 08-24 (later one-off visits on 08-27 are not drawn)
      const st = D.focus.filter((f) => f.agent === A && f.t0 < "2026-08-25");
      const big = [Xt(d3.min(st, (f) => f.t0)), Xt(d3.max(st, (f) => f.t1))];
      const y0 = a.y + (pitch - barH) / 2 - 0.55;
      gf.append("rect").attr("x", big[0]).attr("y", y0).attr("width", big[1] - big[0]).attr("height", barH + 1.1)
        .attr("fill", "none").attr("stroke", C.ink).attr("stroke-width", 0.75);
      const tl = S.text(gf, X("2026-08-13", 0) + 1, a.y + pitch / 2 + 2.0, "in #focus", { size: 5.8, fill: A === 29 ? "#fff" : C.ink }); if (A === 6) S.halo(tl, 1.6);
    }

    // ------------------------------------------------------------------ time axis: one tick per Monday
    const ax = g.append("g").attr("transform", `translate(0,${axY})`);
    ax.append("line").attr("x1", LM).attr("x2", xEnd).attr("stroke", C.ink2).attr("stroke-width", 0.5);
    let prevM = -1;
    days.forEach((d, i) => {
      const t = new Date(d + "T00:00Z");
      if (t.getUTCDay() !== 1 && i !== 0) return;
      ax.append("line").attr("x1", xd[i]).attr("x2", xd[i]).attr("y1", 0).attr("y2", 2.2).attr("stroke", C.ink2).attr("stroke-width", 0.5);
      const m = t.getUTCMonth();
      const s = m !== prevM ? d3.utcFormat("%b %-d")(t) : d3.utcFormat("%-d")(t);
      prevM = m;
      const tt = S.text(ax, xd[i], 8.6, s, { size: 6.6, fill: C.ink2 });
      tt.selectAll("tspan").attr("font-family", F.tick);
    });
    days.forEach((d, i) => ax.append("line").attr("x1", xd[i] + dw / 2).attr("x2", xd[i] + dw / 2).attr("y1", 0).attr("y2", 1.0)
      .attr("stroke", C.ink2).attr("stroke-width", 0.3));
    S.text(ax, LM - 3, 8.6, "2026", { anchor: "end", size: 6.2, fill: C.ink2 });

    // ------------------------------------------------------------------ legend (wraps to a second row)
    const items = D.groups.map((G) => ({ label: G.label, color: COL[G.key] }))
      .concat([{ label: "own artifact", color: COL.own }, { label: "another agent's", color: COL.other },
        { label: "no project named", color: COL.none }]);
    let lx = LM, ly = axY + 18.6;
    for (const it of items) {
      const gi = g.append("g").attr("transform", `translate(${lx},${ly})`);
      gi.append("rect").attr("x", 0).attr("y", -4.4).attr("width", 7.5).attr("height", 5).attr("fill", it.color);
      const t = S.text(gi, 9.5, 0, it.label, { size: 6.2 });
      const w = 9.5 + t.node().getComputedTextLength() + 7.5;
      if (lx + w > W - RM && lx > LM) { gi.attr("transform", `translate(${LM},${ly + 8.6})`); lx = LM + w; ly += 8.6; }
      else lx += w;
    }
    const tri = g.append("g").attr("transform", `translate(${lx},${ly})`);
    tri.append("path").attr("d", "M0,-4.2L2.8,-1.7L0,0.8Z").attr("fill", C.ink);
    S.text(tri, 5, 0, "joins", { size: 6.2 });
    if (ly + 3 > H) console.error("legend overflows: " + ly);
  },
};
