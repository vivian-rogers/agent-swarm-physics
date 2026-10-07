// Sec. III: the AI Village over time. Top strip: 51 goal periods by goal author. Middle: one lane per agent,
// grouped and colored by lab. Bottom: agents present, stacked by lab. Dashed lines A-J: scaffold changes.
// Data: data/processed/paper-figs/timeline.json (export/timeline.py).
window.FIG = {
  width: 7.05, height: 3.42,
  draw(svg, D) {
    const { C, F } = S;
    const W = 7.05 * 72, H = 3.42 * 72;
    const g = svg.append("g");
    const defs = svg.append("defs");
    const P = d3.utcParse("%Y-%m-%d");

    // Okabe-Ito, one hue per lab; the fine-tuned Kimi leaders share Moonshot's hue, hatched
    const LAB = {
      "Anthropic": { c: "#D55E00", name: "Anthropic" },
      "OpenAI": { c: "#0072B2", name: "OpenAI" },
      "Google": { c: "#009E73", name: "Google" },
      "xAI": { c: "#262626", name: "xAI" },
      "DeepSeek": { c: "#56B4E9", name: "DeepSeek" },
      "Moonshot": { c: "#CC79A7", name: "Moonshot" },
      "Fine-tuned (Kimi)": { c: "#CC79A7", name: "fine-tuned Kimi", hatch: true },
      "Zhipu": { c: "#F0E442", name: "Zhipu", edge: "#b8ac1c" },
      "Meta": { c: "#E69F00", name: "Meta" },
    };
    const hp = defs.append("pattern").attr("id", "ftk").attr("patternUnits", "userSpaceOnUse")
      .attr("width", 2.2).attr("height", 2.2).attr("patternTransform", "rotate(45)");
    hp.append("rect").attr("width", 2.2).attr("height", 2.2).attr("fill", "#f3d9e8");
    hp.append("rect").attr("width", 1.0).attr("height", 2.2).attr("fill", "#CC79A7");
    const labFill = (lab) => LAB[lab].hatch ? "url(#ftk)" : LAB[lab].c;

    // goal author: neutral tones so the lab hues carry the eye (O operator, D agents design content, F free,
    // A an agent, P private roles)
    const gp = defs.append("pattern").attr("id", "priv").attr("patternUnits", "userSpaceOnUse")
      .attr("width", 2.6).attr("height", 2.6).attr("patternTransform", "rotate(45)");
    gp.append("rect").attr("width", 2.6).attr("height", 2.6).attr("fill", "#c9c9c9");
    gp.append("rect").attr("width", 1.0).attr("height", 2.6).attr("fill", "#7a7a7a");
    const AUTH = {
      O: { fill: "#c9c9c9", ink: C.ink, label: "operator" },
      D: { fill: "#7a7a7a", ink: "#fff", label: "agents design content" },
      A: { fill: "#2b2b2b", ink: "#fff", label: "an agent" },
      F: { fill: "#ececec", ink: C.ink2, label: "free (holiday)" },
      P: { fill: "url(#priv)", ink: C.ink, label: "private roles" },
    };

    // ------------------------------------------------------------------ geometry
    const LM = 70, RM = 6;
    const x = d3.scaleUtc().domain([P(D.x0), P(D.x1)]).range([LM, W - RM]);
    const yLet = 6.6, sTop = 10, sH = 9;
    const lTop = sTop + sH + 7, pitch = 3.0, barH = 2.15, gGap = 2.6;

    // lanes: grouped by lab (lab order), by joining date inside a group
    const groups = D.lab_order.map((lab) => ({ lab, rows: D.agents.filter((a) => a.lab === lab)
      .sort((a, b) => d3.ascending(a.joined, b.joined) || a.agent - b.agent) })).filter((G) => G.rows.length);
    let yy = lTop;
    for (const G of groups) { G.y0 = yy; yy += G.rows.length * pitch; G.y1 = yy; yy += gGap; }
    const lBot = yy - gGap;
    const rTop = lBot + 3, rY = rTop + 6.2;                  // regime ruler
    const bTop = rY + 7, bBot = H - 13;                    // agents-present panel
    const lineTop = sTop - 1.5, lineBot = bBot;

    // ------------------------------------------------------------------ scaffold-change lines (under everything)
    const gl = g.append("g");
    for (const ch of D.changes) {
      const xc = x(P(ch.date));
      gl.append("line").attr("x1", xc).attr("x2", xc).attr("y1", lineTop).attr("y2", lineBot)
        .attr("stroke", C.ink2).attr("stroke-width", 0.45).attr("stroke-dasharray", "1.6,1.4");
    }
    // letters: spread clusters apart (min 5.6 pt), short leader to the line
    const lets = D.changes.map((ch) => ({ ...ch, x0: x(P(ch.date)), x: x(P(ch.date)) }));
    for (let it = 0; it < 50; it++) {
      for (let i = 1; i < lets.length; i++) {
        const d = lets[i].x - lets[i - 1].x;
        if (d < 5.6) { const s = (5.6 - d) / 2; lets[i].x += s; lets[i - 1].x -= s; }
      }
    }
    for (const L of lets) {
      S.text(g, L.x, yLet, L.letter, { anchor: "middle", size: 6.4, fill: C.ink });
      if (Math.abs(L.x - L.x0) > 0.3) g.append("line").attr("x1", L.x).attr("y1", yLet + 0.9).attr("x2", L.x0)
        .attr("y2", lineTop).attr("stroke", C.ink2).attr("stroke-width", 0.45);
    }

    // ------------------------------------------------------------------ top strip: goal periods
    const gs = g.append("g");
    for (const G of D.goals) {
      const a = x(P(G.start)), b = x(P(G.end)), st = AUTH[G.author];
      gs.append("rect").attr("x", a).attr("y", sTop).attr("width", Math.max(0.3, b - a)).attr("height", sH)
        .attr("fill", st.fill);
      if (b - a >= 9.5) {
        const t = S.text(gs, (a + b) / 2, sTop + sH / 2 + 2.1, String(G.goal), { anchor: "middle", size: 5.9, fill: st.ink });
        t.selectAll("tspan").attr("font-family", F.tick);
        if (G.author === "P") S.halo(t, 1.6);
      }
    }
    for (const G of D.goals.slice(1)) gs.append("line").attr("x1", x(P(G.start))).attr("x2", x(P(G.start)))
      .attr("y1", sTop).attr("y2", sTop + sH).attr("stroke", "#fff").attr("stroke-width", 0.5);
    S.text(g, LM - 4, sTop + sH / 2 + 2.3, "goal periods", { anchor: "end", size: 6.4, fill: C.ink });

    // ------------------------------------------------------------------ middle: agent lanes by lab
    const gm = g.append("g");
    groups.forEach((G, gi) => {
      const L = LAB[G.lab];
      G.rows.forEach((a, i) => {
        const y0 = G.y0 + i * pitch + (pitch - barH) / 2;
        const xa = x(P(a.joined)), xb = x(P(a.left));
        gm.append("rect").attr("x", xa).attr("y", y0).attr("width", Math.max(0.8, xb - xa)).attr("height", barH)
          .attr("fill", labFill(G.lab)).attr("stroke", L.edge || null).attr("stroke-width", L.edge ? 0.25 : null);
      });
      // label block in the margin: swatch, name, count
      const yc = (G.y0 + G.y1) / 2 + 2.0;
      g.append("rect").attr("x", LM - 6.5).attr("y", yc - 4.3).attr("width", 3.6).attr("height", 3.9)
        .attr("fill", labFill(G.lab)).attr("stroke", L.edge || null).attr("stroke-width", L.edge ? 0.25 : null);
      const n = S.text(g, LM - 9, yc, String(G.rows.length), { anchor: "end", size: 6.0, fill: C.muted });
      n.selectAll("tspan").attr("font-family", F.tick);
      S.text(g, LM - 19, yc, L.name, { anchor: "end", size: 6.2, fill: C.ink });
    });

    // goal-author key, in the empty lower-left of the lanes (white card over the dashed lines)
    const kx = x(P("2025-04-08")), ky = groups.find((G) => G.lab === "DeepSeek").y0 + 1.2;
    const items = ["O", "D", "A", "F", "P"];
    const kg = g.append("g").attr("transform", `translate(${kx},${ky})`);
    const card = kg.append("rect").attr("fill", "#fff");
    S.text(kg, 0, 4.6, "goal written by (top strip)", { size: 6.2, fill: C.ink });
    const colX = [0, 86], rowY = [12.6, 20.4, 28.2];
    items.forEach((k, i) => {
      const cx = colX[i < 3 ? 0 : 1], cy = rowY[i < 3 ? i : i - 3];
      kg.append("rect").attr("x", cx).attr("y", cy - 4.6).attr("width", 7).attr("height", 5)
        .attr("fill", AUTH[k].fill).attr("stroke", k === "F" ? "#c9c9c9" : null).attr("stroke-width", 0.3);
      S.text(kg, cx + 9.5, cy, AUTH[k].label, { size: 6.2, fill: C.ink });
    });
    const bb = kg.node().getBBox();
    card.attr("x", bb.x - 2.5).attr("y", bb.y - 1.5).attr("width", bb.width + 5).attr("height", bb.height + 3);

    // ------------------------------------------------------------------ regime ruler
    const gr = g.append("g");
    for (const R of D.regimes) {
      const a = x(P(R.start)) + 1.2, b = Math.min(x(P(R.end)), x(P(D.export))) - 1.2;
      gr.append("path").attr("d", `M${a},${rY - 2.2}V${rY}H${b}V${rY - 2.2}`).attr("fill", "none")
        .attr("stroke", C.ink2).attr("stroke-width", 0.5);
      const lab = R.name === "II" ? "II" : `regime ${R.name}`;
      const t = S.text(gr, (a + b) / 2, rY + 0.2, lab, { anchor: "middle", size: 6.2, fill: C.ink, baseline: "middle" });
      const w = t.node().getComputedTextLength();
      gr.insert("rect", () => t.node()).attr("x", (a + b) / 2 - w / 2 - 1.5).attr("y", rY - 3).attr("width", w + 3)
        .attr("height", 6).attr("fill", "#fff");
    }

    // ------------------------------------------------------------------ bottom: agents present, stacked by lab
    const days = d3.utcDay.range(P(D.goals[0].start), d3.utcDay.offset(P(D.export), 1));
    const labs = groups.map((G) => G.lab);
    const rows = days.map((t) => {
      const r = { t };
      const iso = d3.utcFormat("%Y-%m-%d")(t);
      for (const lab of labs) r[lab] = D.agents.filter((a) => a.lab === lab && a.joined <= iso && iso < a.left).length;
      return r;
    });
    const stack = d3.stack().keys(labs)(rows);
    const nMax = d3.max(rows, (r) => d3.sum(labs, (l) => r[l]));
    const yb = d3.scaleLinear().domain([0, 34]).range([bBot, bTop]);
    if (nMax > 34) throw new Error("agents present exceeds axis: " + nMax);
    const area = d3.area().x((d) => x(d.data.t)).y0((d) => yb(d[0])).y1((d) => yb(d[1])).curve(d3.curveStepAfter);
    const gb = g.append("g");
    S.axis(gb.append("g").attr("transform", `translate(${LM - 2},0)`), yb, "left", { ticks: [0, 10, 20, 30], format: d3.format("d") });
    for (const t of [10, 20, 30]) gb.append("line").attr("x1", LM).attr("x2", W - RM).attr("y1", yb(t)).attr("y2", yb(t))
      .attr("stroke", C.grid).attr("stroke-width", 0.5);
    stack.forEach((s) => gb.append("path").datum(s).attr("d", area).attr("fill", labFill(s.key))
      .attr("stroke", LAB[s.key].edge || "none").attr("stroke-width", LAB[s.key].edge ? 0.25 : 0));
    // total outline
    const tot = d3.line().x((r) => x(r.t)).y((r) => yb(d3.sum(labs, (l) => r[l]))).curve(d3.curveStepAfter);
    gb.append("path").datum(rows).attr("d", tot).attr("fill", "none").attr("stroke", C.ink).attr("stroke-width", 0.6);
    S.text(g, LM - 19, (bTop + bBot) / 2 - 2.2, "agents", { anchor: "end", size: 6.4, fill: C.ink });
    S.text(g, LM - 19, (bTop + bBot) / 2 + 5.4, "present", { anchor: "end", size: 6.4, fill: C.ink });
    // start value (the caption's "from 4 agents")
    const n0 = d3.sum(labs, (l) => rows.find((r) => d3.utcFormat("%Y-%m-%d")(r.t) === D.goals[0].start)[l]);
    S.text(g, x(P(D.goals[0].start)) + 2, yb(n0) - 2.2, String(n0), { size: 6.2, fill: C.ink });

    // time axis
    const ax = g.append("g").attr("transform", `translate(0,${bBot + 0.5})`);
    const ticks = [P("2025-04-01"), P("2025-07-01"), P("2025-10-01"), P("2026-01-01"), P("2026-04-01"), P("2026-07-01")];
    const fmt = (t) => t.getUTCMonth() === 0 || t === ticks[0] ? d3.utcFormat("%b %Y")(t) : d3.utcFormat("%b")(t);
    S.axis(ax, x, "bottom", { ticks, format: fmt });
    // month minor ticks
    for (const t of d3.utcMonth.range(P(D.x0), P(D.x1))) ax.append("line").attr("x1", x(t)).attr("x2", x(t))
      .attr("y1", 0).attr("y2", 1.2).attr("stroke", C.ink2).attr("stroke-width", 0.4);
  },
};
