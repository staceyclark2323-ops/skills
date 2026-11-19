#!/usr/bin/env python3
"""Render a step-by-step decision flowchart (boxes, yes/no diamonds, arrows).

Usage:
    python render_flowchart.py spec.json out_basename [--png]

Writes out_basename.svg and out_basename.html (and out_basename.png with --png,
which needs Playwright + Chromium).

spec.json shape:
{
  "title": "Steps of Writing IEP Goals",
  "subtitle": "optional one-liner",
  "start": "Open the student's IEP in Infinite Campus",
  "steps": [
    {
      "action": "Short verb-first step name",
      "details": ["optional sub-bullet", "another"],
      "check": "Step complete?",               # optional, default shown
      "if_no": "What to do when the answer is No"
    }
  ],
  "end": "Final outcome text"
}
"""
import json, sys, textwrap, html, subprocess
from pathlib import Path

# ---------- layout constants ----------
W = 960
MAIN_X, MAIN_W = 90, 420          # main column (action boxes)
CX = MAIN_X + MAIN_W / 2          # main column centre line
NO_X, NO_W = 610, 300             # right column ("No" fix boxes)
GAP = 34
D_W, D_H = 250, 104               # diamond size
FONT = "Arial, Helvetica, sans-serif"

COL = {
    "ink": "#1f2933", "start": "#d1fae5", "start_s": "#047857",
    "act": "#dbeafe", "act_s": "#1d4ed8", "dia": "#fef3c7", "dia_s": "#b45309",
    "no": "#fee2e2", "no_s": "#b91c1c", "yes": "#047857", "arrow": "#374151",
    "num": "#1d4ed8",
}


def esc(s):
    return html.escape(str(s), quote=True)


def wrap(s, chars):
    return textwrap.wrap(str(s), chars) or [""]


def text_block(lines, x, y, size=15, weight="normal", anchor="middle", fill=None, lh=None):
    lh = lh or size * 1.3
    out = []
    for i, ln in enumerate(lines):
        out.append(
            f'<text x="{x}" y="{y + i * lh}" font-family="{FONT}" font-size="{size}" '
            f'font-weight="{weight}" text-anchor="{anchor}" fill="{fill or COL["ink"]}">{esc(ln)}</text>'
        )
    return "\n".join(out)


def arrow(x1, y1, x2, y2, label=None, lx=None, ly=None, color=None):
    c = color or COL["arrow"]
    s = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="2.2" marker-end="url(#ah)"/>'
    if label:
        s += text_block([label], lx, ly, size=14, weight="bold", fill=c)
    return s


def path_arrow(points, color=None):
    c = color or COL["arrow"]
    d = "M " + " L ".join(f"{x} {y}" for x, y in points)
    return f'<path d="{d}" fill="none" stroke="{c}" stroke-width="2.2" marker-end="url(#ah)"/>'


def render(spec):
    parts, y = [], 30
    # title
    title_lines = wrap(spec.get("title", "Flowchart"), 48)
    parts.append(text_block(title_lines, W / 2, y + 26, size=28, weight="bold"))
    y += 26 + 34 * (len(title_lines) - 1)
    if spec.get("subtitle"):
        sub = wrap(spec["subtitle"], 90)
        parts.append(text_block(sub, W / 2, y + 30, size=15, fill="#52606d"))
        y += 30 + 20 * (len(sub) - 1)
    y += 36

    def oval(label, fill, stroke, y):
        lines = wrap(label, 40)
        h = 30 + 20 * len(lines)
        parts.append(f'<rect x="{MAIN_X}" y="{y}" width="{MAIN_W}" height="{h}" rx="{h/2}" '
                     f'fill="{fill}" stroke="{stroke}" stroke-width="2.5"/>')
        parts.append(text_block(lines, CX, y + h / 2 - 10 * (len(lines) - 1) + 6, size=16,
                                weight="bold"))
        return h

    h = oval("START: " + spec.get("start", "Begin"), COL["start"], COL["start_s"], y)
    y += h

    steps = spec.get("steps", [])
    for i, st in enumerate(steps, 1):
        parts.append(arrow(CX, y, CX, y + GAP - 2))
        y += GAP
        # action box
        head = wrap(f"{st['action']}", 38)
        det = []
        for d in st.get("details", []):
            w = wrap(d, 50)
            det.append("• " + w[0])
            det += ["   " + x for x in w[1:]]
        box_h = 22 + 22 * len(head) + (8 + 18 * len(det) if det else 0) + 12
        box_y = y
        parts.append(f'<rect x="{MAIN_X}" y="{box_y}" width="{MAIN_W}" height="{box_h}" rx="10" '
                     f'fill="{COL["act"]}" stroke="{COL["act_s"]}" stroke-width="2"/>')
        # step number badge
        parts.append(f'<circle cx="{MAIN_X}" cy="{box_y}" r="17" fill="{COL["num"]}"/>')
        parts.append(text_block([str(i)], MAIN_X, box_y + 6, size=16, weight="bold", fill="#fff"))
        parts.append(text_block(head, CX, box_y + 30, size=17, weight="bold", lh=22))
        if det:
            parts.append(text_block(det, MAIN_X + 22, box_y + 30 + 22 * len(head) + 6, size=13.5,
                                    anchor="start", lh=18, fill="#334e68"))
        y = box_y + box_h
        # diamond
        parts.append(arrow(CX, y, CX, y + GAP - 2))
        y += GAP
        dy = y
        pts = f"{CX},{dy} {CX + D_W/2},{dy + D_H/2} {CX},{dy + D_H} {CX - D_W/2},{dy + D_H/2}"
        parts.append(f'<polygon points="{pts}" fill="{COL["dia"]}" stroke="{COL["dia_s"]}" stroke-width="2"/>')
        q = wrap(st.get("check", f"Step {i} complete?"), 20)
        parts.append(text_block(q, CX, dy + D_H / 2 - 9 * (len(q) - 1) + 5, size=14.5, weight="bold", lh=18))
        # NO branch -> fix box -> loop back to action box
        no_lines = wrap(st.get("if_no", "Go back and finish this step"), 32)
        no_h = 20 + 19 * len(no_lines)
        no_y = dy + D_H / 2 - no_h / 2
        parts.append(arrow(CX + D_W / 2, dy + D_H / 2, NO_X - 2, dy + D_H / 2, "No",
                           (CX + D_W / 2 + NO_X) / 2, dy + D_H / 2 - 8, COL["no_s"]))
        parts.append(f'<rect x="{NO_X}" y="{no_y}" width="{NO_W}" height="{no_h}" rx="8" '
                     f'fill="{COL["no"]}" stroke="{COL["no_s"]}" stroke-width="2"/>')
        parts.append(text_block(no_lines, NO_X + NO_W / 2, no_y + 24, size=14, lh=19))
        back_y = box_y + min(box_h / 2, 40)
        parts.append(path_arrow([(NO_X + NO_W / 2, no_y), (NO_X + NO_W / 2, back_y),
                                 (MAIN_X + MAIN_W + 2, back_y)], COL["no_s"]))
        parts.append(text_block(["Fix, then re-check"], NO_X + NO_W / 2 + 8, back_y - 8, size=12.5,
                                anchor="start", fill=COL["no_s"]))
        y = dy + D_H
        # YES label on the way down
        parts.append(text_block(["Yes"], CX + 12, y + GAP / 2 + 5, size=14, weight="bold",
                                anchor="start", fill=COL["yes"]))

    parts.append(arrow(CX, y, CX, y + GAP - 2, color=COL["yes"]))
    y += GAP
    h = oval("DONE: " + spec.get("end", "Finished"), COL["start"], COL["start_s"], y)
    y += h + 40

    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {y}" width="{W}" height="{y}">'
           f'<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
           f'orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="context-stroke"/></marker></defs>'
           f'<rect width="100%" height="100%" fill="#ffffff"/>' + "\n".join(parts) + "</svg>")
    return svg, y


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    spec = json.loads(Path(sys.argv[1]).read_text())
    out = Path(sys.argv[2])
    svg, h = render(spec)
    out.with_suffix(".svg").write_text(svg)
    page = (f'<!doctype html><html><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{esc(spec.get("title", "Flowchart"))}</title>'
            f'<style>body{{margin:0;background:#fff;}}svg{{display:block;max-width:100%;height:auto;margin:0 auto;}}'
            f'@media print{{svg{{width:100%;}}}}</style></head><body>{svg}</body></html>')
    out.with_suffix(".html").write_text(page)
    print(f"wrote {out.with_suffix('.svg')} and {out.with_suffix('.html')}")
    if "--png" in sys.argv:
        html_uri = out.with_suffix(".html").resolve().as_uri()
        png = str(out.with_suffix(".png"))
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                b = p.chromium.launch()
                pg = b.new_page(viewport={"width": W, "height": int(h)}, device_scale_factor=2)
                pg.goto(html_uri)
                pg.screenshot(path=png, full_page=True)
                b.close()
        except ImportError:  # fall back to Node's Playwright
            js = ("const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();"
                  f"const p=await b.newPage({{viewport:{{width:{W},height:{int(h)}}},deviceScaleFactor:2}});"
                  f"await p.goto('{html_uri}');await p.screenshot({{path:'{png}',fullPage:true}});"
                  "await b.close();})();")
            root = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip()
            subprocess.run(["node", "-e", js], check=True, env={**__import__("os").environ, "NODE_PATH": root})
        print(f"wrote {png}")

if __name__ == "__main__":
    main()
