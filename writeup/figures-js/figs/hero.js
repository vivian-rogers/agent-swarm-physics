// Page-1 figure (one column, small): the AI Village as a spin network at one moment of goal 51.
// Red = talking, blue = working, white = no call; gray arcs = named messages (couplings); orange = fields.
// Data: hero.json (export/hero.py).
window.FIG = {
  width: 3.40, height: 2.05,
  draw(svg, D) {
    const { C } = S;
    const W = 3.40 * 72, H = 2.05 * 72;
    const g = svg.append("g");
    const defs = svg.append("defs");
    const A = { w: W, h: H - 13 };
    const cx = A.w / 2, cy = A.h / 2 + 1;

    const rg = defs.append("radialGradient").attr("id", "fieldwash");
    rg.append("stop").attr("offset", "0%").attr("stop-color", C.field).attr("stop-opacity", 0.20);
    rg.append("stop").attr("offset", "65%").attr("stop-color", C.field).attr("stop-opacity", 0.10);
    rg.append("stop").attr("offset", "100%").attr("stop-color", C.field).attr("stop-opacity", 0);
    g.append("ellipse").attr("cx", cx).attr("cy", cy).attr("rx", 104).attr("ry", 62).attr("fill", "url(#fieldwash)");

    const nodes = D.nodes.map((d) => ({ ...d }));
    const byId = new Map(nodes.map((d) => [d.id, d]));
    const links = D.links.filter((l) => byId.has(l.source) && byId.has(l.target)).map((l) => ({ ...l }));
    const rad = d3.scaleSqrt().domain([0, d3.max(nodes, (d) => d.msgs)]).range([2.0, 5.0]);
    nodes.forEach((d, i) => { const r = 9 * Math.sqrt(i + 0.5), a = i * Math.PI * (3 - Math.sqrt(5)); d.x = cx + r * Math.cos(a); d.y = cy + r * Math.sin(a); });
    const sim = d3.forceSimulation(nodes)
      .force("link", d3.forceLink(links).id((d) => d.id).distance(46).strength((l) => Math.min(0.35, 0.03 + 0.02 * l.n)))
      .force("charge", d3.forceManyBody().strength(-70).distanceMax(160))
      .force("x", d3.forceX(cx).strength(0.10)).force("y", d3.forceY(cy).strength(0.16))
      .force("collide", d3.forceCollide((d) => rad(d.msgs) + 2.2))
      .stop();
    for (let i = 0; i < 600; i++) sim.tick();
    const xs = d3.extent(nodes, (d) => d.x), ys = d3.extent(nodes, (d) => d.y);
    const sx = 150 / (xs[1] - xs[0]), sy = (A.h - 22) / (ys[1] - ys[0]);
    nodes.forEach((d) => { d.x = cx + (d.x - (xs[0] + xs[1]) / 2) * sx; d.y = cy + (d.y - (ys[0] + ys[1]) / 2) * sy; });

    const wl = d3.scaleSqrt().domain([1, d3.max(links, (l) => l.n)]).range([0.22, 1.6]);
    const al = d3.scaleLinear().domain([1, d3.max(links, (l) => l.n)]).range([0.28, 0.75]);
    g.append("g").selectAll("path").data(links.sort((a, b) => a.n - b.n)).join("path")
      .attr("d", (l) => {
        const dx = l.target.x - l.source.x, dy = l.target.y - l.source.y, dr = Math.hypot(dx, dy) * 1.6;
        return `M${l.source.x},${l.source.y}A${dr},${dr} 0 0,1 ${l.target.x},${l.target.y}`;
      })
      .attr("fill", "none").attr("stroke", C.ink2).attr("stroke-width", (l) => wl(l.n)).attr("stroke-opacity", (l) => al(l.n))
      .attr("stroke-linecap", "round");
    const col = { up: C.up, down: C.down, off: "#fff" };
    g.append("g").selectAll("circle").data(nodes).join("circle")
      .attr("cx", (d) => d.x).attr("cy", (d) => d.y).attr("r", (d) => rad(d.msgs))
      .attr("fill", (d) => col[d.state]).attr("stroke", (d) => d.state === "off" ? C.muted : "#fff")
      .attr("stroke-width", (d) => d.state === "off" ? 0.6 : 0.7);

    defs.append("marker").attr("id", "farrow").attr("viewBox", "0 0 6 6").attr("refX", 5).attr("refY", 3)
      .attr("markerWidth", 4.2).attr("markerHeight", 4.2).attr("orient", "auto")
      .append("path").attr("d", "M0,0L6,3L0,6z").attr("fill", C.field);
    const src = [
      { label: "goal text", x: 1, y: 7, ax: 34, ay: 20, anchor: "start" },
      { label: "timetable", x: A.w - 1, y: 7, ax: A.w - 34, ay: 20, anchor: "end" },
      { label: "room", x: 1, y: A.h - 1, ax: 30, ay: A.h - 13, anchor: "start" },
      { label: "own style", x: A.w - 1, y: A.h - 1, ax: A.w - 32, ay: A.h - 13, anchor: "end" },
    ];
    for (const f of src) {
      S.text(g, f.x, f.y, f.label, { anchor: f.anchor, size: 6.3, fill: "#9a6500" });
      const x0 = f.anchor === "start" ? f.x + 8 : f.x - 8, y0 = f.y < A.h / 2 ? f.y + 3 : f.y - 9;
      g.append("line").attr("x1", x0).attr("y1", y0).attr("x2", f.ax).attr("y2", f.ay)
        .attr("stroke", C.field).attr("stroke-width", 1.1).attr("marker-end", "url(#farrow)");
    }

    S.legend(g, 2, H - 2.5, [
      { label: "talking", color: C.up, size: 14 },
      { label: "working", color: C.down, size: 14 },
      { label: "no call", color: "#fff", stroke: C.muted, sw: 0.55, size: 12 },
      { label: "named message", line: true, color: C.ink2, width: 1.0 },
      { label: "field", line: true, color: C.field, width: 1.2 },
    ], { gap: 8, size: 6.2 });
  },
};
