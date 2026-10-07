// Page-1 figure (one column): the AI Village as a spin system, goal period 51, one moment on 2026-09-04.
// Left: the 32 agents on a ring grouped by lab (all nodes the same size). Fill = spin state in the last 10 min
// (red talk, blue work, white no call). Chords = named messages: faint for the whole day, dark for those sent in
// the 10-min window. Orange ring = fields, which reach every agent at once.
// Right: the three numbers behind the picture, regime III (paper Secs. II-IV): named vs unnamed read (H67),
// loop gain g (H67), field share of co-activation (H38, fragile).
// Data: hero.json (export/hero.py).
window.FIG = {
  width: 3.40, height: 2.72,
  draw(svg, D) {
    const { C } = S;
    const W = 3.40 * 72, H = 2.72 * 72;
    const g = svg.append("g");
    const defs = svg.append("defs");

    // ------------------------------------------------------------------ ring
    const cx = 94, cy = 89, R = 39, rN = 2.9;
    const LAB_ORDER = ["Anthropic", "OpenAI", "Google", "DeepSeek", "Zhipu", "Moonshot", "xAI", "Meta"];
    const short = (n) => n.replace(/^Claude /, "").replace(/^DeepSeek-/, "DeepSeek ");
    const nodes = D.nodes.map((d) => ({ ...d, short: short(d.name) }));
    nodes.sort((a, b) => (LAB_ORDER.indexOf(a.lab) - LAB_ORDER.indexOf(b.lab)) || (a.id - b.id));
    const labs = LAB_ORDER.filter((l) => nodes.some((n) => n.lab === l));
    const gapSlots = 1.0, nSlots = nodes.length + gapSlots * labs.length;
    let slot = 0, prevLab = null;
    nodes.forEach((n) => {
      if (n.lab !== prevLab) { slot += gapSlots; prevLab = n.lab; }
      n.a = -Math.PI / 2 + (2 * Math.PI * (slot + 0.5)) / nSlots;
      n.x = cx + R * Math.cos(n.a); n.y = cy + R * Math.sin(n.a);
      slot += 1;
    });
    const byId = new Map(nodes.map((n) => [n.id, n]));

    // field: an orange ring just outside the agents, with a short spoke to each agent
    g.append("circle").attr("cx", cx).attr("cy", cy).attr("r", R + 7.5).attr("fill", "none")
      .attr("stroke", C.field).attr("stroke-width", 1.6).attr("stroke-opacity", 0.9);
    nodes.forEach((n) => {
      g.append("line").attr("x1", cx + (R + 6.6) * Math.cos(n.a)).attr("y1", cy + (R + 6.6) * Math.sin(n.a))
        .attr("x2", cx + (R + rN + 0.6) * Math.cos(n.a)).attr("y2", cy + (R + rN + 0.6) * Math.sin(n.a))
        .attr("stroke", C.field).attr("stroke-width", 0.7);
    });

    // chords: quadratic curves pulled toward the centre
    const chord = (s, t) => {
      const k = 0.18, mx = cx + ((s.x + t.x) / 2 - cx) * k, my = cy + ((s.y + t.y) / 2 - cy) * k;
      return `M${s.x},${s.y}Q${mx},${my} ${t.x},${t.y}`;
    };
    const day = D.links.filter((l) => byId.has(l.source) && byId.has(l.target));
    const wDay = d3.scaleSqrt().domain([1, d3.max(day, (l) => l.n)]).range([0.2, 1.3]);
    g.append("g").selectAll("path").data(day).join("path")
      .attr("d", (l) => chord(byId.get(l.source), byId.get(l.target)))
      .attr("fill", "none").attr("stroke", "#b9b9b9").attr("stroke-width", (l) => wDay(l.n)).attr("stroke-opacity", 0.55);
    defs.append("marker").attr("id", "nowarrow").attr("viewBox", "0 0 6 6").attr("refX", 5.6).attr("refY", 3)
      .attr("markerWidth", 3.6).attr("markerHeight", 3.6).attr("orient", "auto").attr("markerUnits", "userSpaceOnUse")
      .append("path").attr("d", "M0,0.6L6,3L0,5.4z").attr("fill", C.ink);
    const now = D.links_now.filter((l) => byId.has(l.source) && byId.has(l.target));
    const wNow = d3.scaleSqrt().domain([1, d3.max(now, (l) => l.n)]).range([0.55, 1.6]);
    g.append("g").selectAll("path").data(now.sort((a, b) => a.n - b.n)).join("path")
      .attr("d", (l) => {   // stop short of the target node so the arrowhead shows
        const s = byId.get(l.source), t = byId.get(l.target);
        const k = 0.18, mx = cx + ((s.x + t.x) / 2 - cx) * k, my = cy + ((s.y + t.y) / 2 - cy) * k;
        const dx = t.x - mx, dy = t.y - my, d = Math.hypot(dx, dy), ex = t.x - dx / d * (rN + 0.9), ey = t.y - dy / d * (rN + 0.9);
        return `M${s.x},${s.y}Q${mx},${my} ${ex},${ey}`;
      })
      .attr("fill", "none").attr("stroke", C.ink).attr("stroke-width", (l) => wNow(l.n)).attr("stroke-opacity", 0.85)
      .attr("marker-end", "url(#nowarrow)");

    // agents: all the same size
    const fill = { up: C.up, down: C.down, off: "#fff" };
    g.append("g").selectAll("circle").data(nodes).join("circle")
      .attr("cx", (n) => n.x).attr("cy", (n) => n.y).attr("r", rN)
      .attr("fill", (n) => fill[n.state]).attr("stroke", (n) => n.state === "off" ? C.ink2 : "#fff")
      .attr("stroke-width", (n) => n.state === "off" ? 0.55 : 0.6);

    // model names, radial, outside the field ring
    nodes.forEach((n) => {
      const deg = n.a * 180 / Math.PI, flip = Math.cos(n.a) < 0;
      const rr = R + 10.5;
      const x = cx + rr * Math.cos(n.a), y = cy + rr * Math.sin(n.a);
      g.append("text").attr("x", x).attr("y", y).attr("font-family", S.F.tick).attr("font-size", 4.9)
        .attr("fill", C.ink2).attr("dominant-baseline", "central").attr("text-anchor", flip ? "end" : "start")
        .attr("transform", `rotate(${flip ? deg + 180 : deg},${x},${y})`).text(n.short);
    });
    // ------------------------------------------------------------------ the three numbers (regime III)
    const X = 176, bw = 46;
    const block = (y, title) => S.text(g, X, y, title, { size: 6.0, fill: C.ink });
    S.text(g, X, 18, "Regime III, all periods", { size: 5.6, fill: C.muted });

    // 1. a read with the reader's name vs without
    block(32, "Talk added by one read");
    const xb = d3.scaleLinear().domain([0, 0.079]).range([0, bw]);
    [["named", 0.079, C.coupling], ["unnamed", 0.004, C.couplingSoft]].forEach(([lab, v, col], i) => {
      const yy = 37 + i * 9.5;
      g.append("rect").attr("x", X).attr("y", yy).attr("width", Math.max(0.8, xb(v))).attr("height", 5.6).attr("rx", 0.6).attr("fill", col);
      if (i === 0) S.text(g, X + 2, yy + 4.5, `named ${v.toFixed(3)}`, { size: 5.3, fill: "#fff" });
      else S.text(g, X + Math.max(0.8, xb(v)) + 2, yy + 4.6, `unnamed ${v.toFixed(3)}`, { size: 5.3, fill: C.ink2 });
    });
    S.text(g, X, 64, "a name: ×19", { size: 5.6, fill: C.coupling });

    // 2. loop gain against the critical point
    block(82, "Echo gain $g$ per message");
    const xg = d3.scaleLinear().domain([0, 1.05]).range([0, bw]);
    g.append("rect").attr("x", X).attr("y", 87).attr("width", xg(1.05)).attr("height", 5.6).attr("fill", C.nullBand);
    g.append("rect").attr("x", X).attr("y", 87).attr("width", xg(0.13)).attr("height", 5.6).attr("rx", 0.6).attr("fill", C.coupling);
    g.append("line").attr("x1", X + xg(1)).attr("x2", X + xg(1)).attr("y1", 85).attr("y2", 94.6).attr("stroke", C.up).attr("stroke-width", 0.9);
    S.text(g, X + xg(0.13) + 2, 91.6, "0.13", { size: 5.4, fill: C.ink2 });
    S.text(g, X + xg(1), 101, "1: runaway", { size: 5.2, fill: C.up, anchor: "end" });

    // 3. field share of co-activation
    block(119, "Joint activity set by");
    S.text(g, X, 126, "the timetable (a field)", { size: 6.0, fill: C.ink });
    const xf = d3.scaleLinear().domain([0, 1]).range([0, bw]);
    g.append("rect").attr("x", X).attr("y", 130).attr("width", xf(1)).attr("height", 5.6).attr("fill", C.nullBand);
    g.append("rect").attr("x", X).attr("y", 130).attr("width", xf(0.72)).attr("height", 5.6).attr("rx", 0.6).attr("fill", C.field);
    S.text(g, X + xf(0.72) + 2, 134.6, "72%", { size: 5.4, fill: C.ink2 });

    // ------------------------------------------------------------------ legend under both
    S.legend(g, 1, H - 13, [
      { label: "talking", color: C.up, size: 12 },
      { label: "working", color: C.down, size: 12 },
      { label: "no call", color: "#fff", stroke: C.ink2, sw: 0.55, size: 11 },
      { label: "fields", line: true, color: C.field, width: 1.8 },
    ], { gap: 8, size: 5.8 });
    S.legend(g, 1, H - 3.5, [
      { label: `named messages in these 10 min (${d3.sum(now, (l) => l.n)})`, line: true, color: C.ink, width: 1.1 },
      { label: "that day", line: true, color: "#b9b9b9", width: 1.1 },
    ], { gap: 8, size: 5.8 });
  },
};
