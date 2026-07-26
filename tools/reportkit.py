#!/usr/bin/env python3
"""Shared editorial design system for report PDFs (extracted from Bloom build_report.py).
Product-agnostic: import tokens + helpers, override palette per product.

Usage:
    import sys; sys.path.insert(0, 'tools')
    from reportkit import *
    nav, navc = make_nav(['Tab1','Tab2'], 'Product <b>Report</b>')
    pages = [f'<div class="page">{nav("Tab1",1,2)} ... {foot("L","R")}</div>']
    render('\n'.join(pages), Path('out.html'), Path('out.pdf'))
"""
import subprocess, pathlib

TERRA   = '#C4603C'
TERRA_D = '#9E4A2C'
SAGE    = '#7C8B6F'
SAGE_D  = '#5F6F54'
BLUSH   = '#E8B4A0'
CREAM   = '#FAF6F0'
CARD    = '#FFFFFF'
INK     = '#2B2620'
MUTED   = '#8A7F70'
LINE    = '#E5DCCB'
MINT    = '#E4EBDD'
BUTTER  = '#F6EBCB'
LAV     = '#E7E2F0'
SKY     = '#DEE9EE'
PEACH   = '#F5DFCE'

CSS = f"""
@page {{ size: 11.69in 8.27in; margin: 0; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html,body {{ background:{CREAM}; }}
body {{ font-family:'Inter',sans-serif; color:{INK}; -webkit-print-color-adjust:exact; print-color-adjust:exact; }}
.page {{ width:1122px; height:794px; position:relative; overflow:hidden; background:{CREAM};
  page-break-after:always; break-after:page; padding:64px 72px 56px; }}
.page:last-child {{ page-break-after:auto; break-after:auto; }}
h1,h2,h3,.serif {{ font-family:'Fraunces',serif; font-weight:400; }}
.eyebrow {{ font-size:11px; letter-spacing:2.6px; text-transform:uppercase; color:{TERRA}; font-weight:600; }}
.eyebrow.sage {{ color:{SAGE_D}; }}
.rule {{ width:56px; height:4px; border-radius:2px; background:{TERRA}; margin:14px 0 22px; }}
.rule.sage {{ background:{SAGE}; }}
.nav {{ display:flex; align-items:center; gap:6px; margin-bottom:30px; }}
.nav .brand {{ font-family:'Fraunces',serif; font-size:15px; margin-right:18px; color:{INK}; white-space:nowrap; }}
.nav .brand b {{ color:{TERRA}; font-weight:600; }}
.nav .tab {{ font-size:10.5px; letter-spacing:1.4px; text-transform:uppercase; color:{MUTED};
  padding:6px 12px; border-radius:999px; white-space:nowrap; }}
.nav .tab.on {{ background:{INK}; color:{CREAM}; }}
.nav .pg {{ margin-left:auto; font-size:10.5px; color:{MUTED}; letter-spacing:1px; white-space:nowrap; }}
.nav.compact .brand {{ font-size:14px; }}
.card {{ background:{CARD}; border:1px solid {LINE}; border-radius:18px; padding:22px 24px; }}
.bignum {{ font-family:'Fraunces',serif; font-size:52px; line-height:1; color:{INK}; }}
.bignum small {{ font-size:26px; }}
.lbl {{ font-size:11px; letter-spacing:1.6px; text-transform:uppercase; color:{MUTED}; margin-top:8px; font-weight:600; }}
.sub {{ font-size:12.5px; color:{MUTED}; line-height:1.55; }}
.body {{ font-size:13.5px; line-height:1.75; color:{INK}; }}
.body + .body {{ margin-top:12px; }}
.body b {{ font-weight:600; }}
.quote {{ font-family:'Fraunces',serif; font-style:italic; font-size:17.5px; line-height:1.55; color:{INK}; }}
.qattr {{ font-size:11px; letter-spacing:1.4px; text-transform:uppercase; color:{MUTED}; margin-top:10px; font-style:normal; font-family:'Inter',sans-serif; }}
.vdiv {{ width:1px; background:{LINE}; align-self:stretch; }}
table {{ border-collapse:collapse; width:100%; }}
th {{ font-size:10px; letter-spacing:1.6px; text-transform:uppercase; color:{MUTED}; text-align:left;
  padding:0 10px 8px; border-bottom:1.5px solid {INK}; font-weight:600; }}
td {{ font-size:12.5px; padding:7px 10px; border-bottom:1px solid {LINE}; }}
tr.hl td {{ background:{PEACH}; }}
td.num, th.num {{ text-align:right; font-variant-numeric:tabular-nums; }}
.tag {{ display:inline-block; font-size:10px; letter-spacing:1px; text-transform:uppercase; font-weight:600;
  padding:3px 9px; border-radius:999px; }}
.tag.terra {{ background:{PEACH}; color:{TERRA_D}; }}
.tag.sage {{ background:{MINT}; color:{SAGE_D}; }}
.tag.butter {{ background:{BUTTER}; color:#6E5716; }}
.tag.lav {{ background:{LAV}; color:#5B4E7A; }}
.tag.red {{ background:#F3D7D0; color:#9E3A26; }}
.pill-cta {{ display:inline-block; background:{TERRA}; color:#fff; font-size:12px; font-weight:600;
  padding:8px 18px; border-radius:999px; letter-spacing:0.4px; }}
.footnote {{ position:absolute; left:72px; right:72px; bottom:26px; font-size:10px; color:{MUTED};
  display:flex; justify-content:space-between; letter-spacing:0.3px; }}
"""

def line_chart(data, w=980, h=250, color=TERRA, fill=True, label_every=5, labels=None):
    pad_l, pad_r, pad_t, pad_b = 34, 12, 14, 26
    cw, ch = w - pad_l - pad_r, h - pad_t - pad_b
    mx, mn = max(data), min(data)
    rng = (mx - mn) or 1
    xs = [pad_l + i * cw / (len(data) - 1) for i in range(len(data))]
    ys = [pad_t + ch - (v - mn) / rng * ch for v in data]
    pts = ' '.join(f'{x:.1f},{y:.1f}' for x, y in zip(xs, ys))
    area = f'{pad_l},{pad_t+ch} ' + pts + f' {pad_l+cw},{pad_t+ch}'
    s = [f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}">']
    for i in range(4):
        gy = pad_t + ch * i / 3
        val = mx - (mx - mn) * i / 3
        s.append(f'<line x1="{pad_l}" y1="{gy:.1f}" x2="{pad_l+cw}" y2="{gy:.1f}" stroke="{LINE}" stroke-width="1"/>')
        s.append(f'<text x="{pad_l-8}" y="{gy+4:.1f}" font-size="9.5" fill="{MUTED}" text-anchor="end" font-family="Inter">{val:.0f}</text>')
    if fill:
        s.append(f'<polygon points="{area}" fill="{color}" opacity="0.10"/>')
    s.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>')
    peak_i = data.index(mx)
    s.append(f'<circle cx="{xs[peak_i]:.1f}" cy="{ys[peak_i]:.1f}" r="4.5" fill="{color}"/>')
    s.append(f'<text x="{xs[peak_i]:.1f}" y="{ys[peak_i]-10:.1f}" font-size="10" fill="{color}" text-anchor="middle" font-weight="600" font-family="Inter">{mx:,}</text>')
    if labels:
        for i, lab in enumerate(labels):
            if i % label_every == 0 or i == len(labels) - 1:
                s.append(f'<text x="{xs[i]:.1f}" y="{h-4}" font-size="9.5" fill="{MUTED}" text-anchor="middle" font-family="Inter">{lab}</text>')
    s.append('</svg>')
    return ''.join(s)

def hbars(items, w=460, row_h=34, color=TERRA, max_v=None, unit=''):
    """items: [(label, value)]"""
    max_v = max_v or max(v for _, v in items) or 1
    rows = []
    for lab, v in items:
        bw = max(2, int((v / max_v) * (w - 190)))
        rows.append(
            f'<div style="display:flex;align-items:center;height:{row_h}px;">'
            f'<div style="width:150px;font-size:12px;color:{INK};overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{lab}</div>'
            f'<div style="width:{bw}px;height:16px;background:{color};border-radius:3px;opacity:0.85;"></div>'
            f'<div style="margin-left:10px;font-size:12px;font-weight:600;color:{INK};font-variant-numeric:tabular-nums;">{v}{unit}</div>'
            f'</div>')
    return '<div>' + ''.join(rows) + '</div>'

def donut(items, size=210, cx_lab='', cx_sub=''):
    """items: [(label, value, color)]"""
    import math
    total = sum(v for _, v, _ in items) or 1
    cx = cy = size / 2
    r = size / 2 - 8
    ir = r * 0.62
    s = [f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">']
    a0 = -math.pi / 2
    for lab, v, color in items:
        frac = v / total
        a1 = a0 + frac * 2 * math.pi
        large = 1 if (a1 - a0) > math.pi else 0
        x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
        x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
        xi1, yi1 = cx + ir * math.cos(a1), cy + ir * math.sin(a1)
        xi0, yi0 = cx + ir * math.cos(a0), cy + ir * math.sin(a0)
        s.append(f'<path d="M{x0:.1f},{y0:.1f} A{r},{r} 0 {large} 1 {x1:.1f},{y1:.1f} L{xi1:.1f},{yi1:.1f} A{ir},{ir} 0 {large} 0 {xi0:.1f},{yi0:.1f} Z" fill="{color}"/>')
        a0 = a1
    s.append(f'<text x="{cx}" y="{cy-2}" font-size="26" font-family="Fraunces,serif" fill="{INK}" text-anchor="middle">{cx_lab}</text>')
    s.append(f'<text x="{cx}" y="{cy+16}" font-size="9" letter-spacing="1.5" fill="{MUTED}" text-anchor="middle" font-family="Inter">{cx_sub}</text>')
    s.append('</svg>')
    return ''.join(s)

def make_nav(tab_names, brand):
    def nav(active, pg, total):
        tabs = ''.join(
            f'<span class="tab{" on" if t == active else ""}">{t}</span>' for t in tab_names)
        return (f'<div class="nav"><div class="brand">{brand}</div>{tabs}'
                f'<span class="pg">{pg:02d} / {total}</span></div>')
    def nav_compact(active, pg, total):
        i = tab_names.index(active) if active in tab_names else 0
        window = tab_names[max(0, i - 2):i + 3]
        tabs = ''.join(
            f'<span class="tab{" on" if t == active else ""}">{t}</span>' for t in window)
        return (f'<div class="nav compact"><div class="brand">{brand}</div>{tabs}'
                f'<span class="pg">{pg:02d} / {total}</span></div>')
    return nav, nav_compact

def foot(left, right):
    return f'<div class="footnote"><span>{left}</span><span>{right}</span></div>'

def render(html_pages, out_html: pathlib.Path, out_pdf: pathlib.Path, css=CSS):
    out_html = pathlib.Path(out_html)
    out_pdf = pathlib.Path(out_pdf)
    out_html.parent.mkdir(parents=True, exist_ok=True)
    doc = (f'<!DOCTYPE html><html><head><meta charset="utf-8">'
           f'<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400..700;1,9..144,400..700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">'
           f'<style>{css}</style></head><body>{html_pages}</body></html>')
    out_html.write_text(doc)
    print(f'HTML written: {out_html} ({len(doc):,} chars, {doc.count("page")} pages)')
    for exe in ('chromium', 'chromium-browser', 'google-chrome'):
        try:
            r = subprocess.run([
                exe, '--headless', '--disable-gpu', '--no-sandbox',
                f'--print-to-pdf={out_pdf}', '--no-pdf-header-footer',
                '--virtual-time-budget=12000', str(out_html)],
                capture_output=True, text=True, timeout=180)
            if r.returncode == 0 and out_pdf.exists():
                print(f'chromium rc: 0\nPDF exists: True {out_pdf.stat().st_size}')
                return
            print(f'{exe} rc={r.returncode}: {r.stderr[-300:]}')
        except FileNotFoundError:
            continue
    raise RuntimeError('no chromium variant succeeded')
