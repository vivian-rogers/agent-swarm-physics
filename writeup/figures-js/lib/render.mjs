// Render D3 figures to vector PDF (for LaTeX) and a 3x PNG preview, with headless Chrome.
//
//   node lib/render.mjs <name> [<name> ...]     # figs/<name>.js + data/processed/paper-figs/<name>.json
//   node lib/render.mjs --all
//
// A figure file sets window.FIG = { width: inches, height: inches, draw(svg, data), data?: '<other name>' }. The svg viewBox is in
// points; lib/style.js (window.S) gives fonts, colors and axis helpers. Outputs:
//   writeup/paper/figs/js/<name>.pdf   (vector; fonts embedded)
//   writeup/figures-js/build/<name>.png  (preview for review only)
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import puppeteer from "puppeteer-core";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const PROJ = path.resolve(HERE, "..");
const ROOT = path.resolve(PROJ, "../..");
const DATA = path.join(ROOT, "data/processed/paper-figs");
const OUT = path.join(ROOT, "writeup/paper/figs/js");
const BUILD = path.join(PROJ, "build");
const LM = "/usr/local/texlive/2025basic/texmf-dist/fonts/opentype/public";
const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";

const face = (fam, file) => `@font-face{font-family:${fam};src:url("file://${LM}/${file}") format("opentype");}`;
const FONTS = [
  face("LM8", "lm/lmroman8-regular.otf"), face("LM8i", "lm/lmroman8-italic.otf"), face("LM8b", "lm/lmroman8-bold.otf"),
  face("LM7", "lm/lmroman7-regular.otf"), face("LM10", "lm/lmroman10-regular.otf"), face("LMSans8", "lm/lmsans8-regular.otf"),
  face("LMMath", "lm-math/latinmodern-math.otf"),
].join("\n");

// "name@v" renders figs/name.js with window.VARIANT = "v" into name_v.pdf (one script, several pages of a figure)
function page(name) {
  const [file, variant] = name.split("@");
  return `<!doctype html><html><head><meta charset="utf-8"><style>
${FONTS}
html,body{margin:0;padding:0;background:#fff}
svg{display:block;font-family:LM8,LMMath,serif;text-rendering:geometricPrecision}
</style>
<script src="file://${PROJ}/node_modules/d3/dist/d3.min.js"></script>
<script src="file://${PROJ}/lib/style.js"></script>
<script>window.VARIANT = ${JSON.stringify(variant || null)};</script>
<script src="file://${PROJ}/figs/${file}.js"></script>
</head><body></body></html>`;
}

async function renderOne(browser, spec) {
  const name = spec.replace("@", "_");
  fs.mkdirSync(BUILD, { recursive: true });
  const html = path.join(BUILD, `${name}.html`);
  fs.writeFileSync(html, page(spec));
  const p = await browser.newPage();
  const errs = [];
  p.on("pageerror", (e) => errs.push(String(e)));
  p.on("console", (m) => { if (m.type() === "error" || m.type() === "warning") errs.push(m.text()); else console.log(`  [${name}] ${m.text()}`); });
  await p.goto(`file://${html}`, { waitUntil: "load" });
  const dataName = (await p.evaluate(() => window.FIG && window.FIG.data)) || spec.split("@")[0];   // FIG.data reuses another figure's JSON
  const dataFile = path.join(DATA, `${dataName}.json`);
  const data = fs.existsSync(dataFile) ? JSON.parse(fs.readFileSync(dataFile, "utf8")) : null;
  const size = await p.evaluate(async (data) => {
    await Promise.all(["LM8", "LM8i", "LM8b", "LM7", "LMMath", "LMSans8"].map((f) => document.fonts.load(`10px ${f}`, "aβ−")));
    await document.fonts.ready;
    const F = window.FIG;
    const svg = d3.select("body").append("svg").attr("xmlns", "http://www.w3.org/2000/svg")
      .attr("width", `${F.width}in`).attr("height", `${F.height}in`)
      .attr("viewBox", `0 0 ${F.width * 72} ${F.height * 72}`);
    await F.draw(svg, data);
    return { w: F.width, h: F.height };
  }, data);
  if (errs.length) { console.error(`${name}: ${errs.join("\n")}`); }
  fs.mkdirSync(OUT, { recursive: true });
  await p.addStyleTag({ content: `@page{size:${size.w}in ${size.h}in;margin:0}` });
  await p.pdf({ path: path.join(OUT, `${name}.pdf`), width: `${size.w}in`, height: `${size.h}in`, printBackground: true,
    preferCSSPageSize: true, pageRanges: "1" });
  await p.setViewport({ width: Math.ceil(size.w * 96), height: Math.ceil(size.h * 96), deviceScaleFactor: 3 });
  await p.screenshot({ path: path.join(BUILD, `${name}.png`), clip: { x: 0, y: 0, width: size.w * 96, height: size.h * 96 } });
  await p.close();
  console.log(`${name}: ${size.w}x${size.h} in -> ${path.relative(ROOT, path.join(OUT, name + ".pdf"))}${errs.length ? " (with errors)" : ""}`);
  return errs.length === 0;
}

const args = process.argv.slice(2);
const names = args.includes("--all")
  ? fs.readdirSync(path.join(PROJ, "figs")).filter((f) => f.endsWith(".js")).map((f) => f.slice(0, -3))
  : args;
if (!names.length) { console.error("usage: node lib/render.mjs <name>... | --all"); process.exit(2); }
const browser = await puppeteer.launch({ executablePath: CHROME, headless: true,
  args: ["--allow-file-access-from-files", "--font-render-hinting=none", "--disable-gpu"] });
let ok = true;
for (const n of names) ok = (await renderOne(browser, n)) && ok;
await browser.close();
process.exit(ok ? 0 : 1);
