#!/usr/bin/env python3
"""Render a 5-band research roadmap (.drawio) from a content JSON file.

Usage:
    python3 render_roadmap.py content.json -o out.drawio
    python3 render_roadmap.py content.json --check      # capacity check only, no write

Geometry is a fixed 954x1296 template measured from a reference figure; only the
number of items inside each family is variable (2-5 depending on the family).
All text capacity is checked before writing: CJK glyph = fontSize px wide,
latin/space = fontSize/2. Overflowing slots are reported with the exact budget.
"""
import argparse
import html
import json
import pathlib
import sys
import unicodedata

# ----------------------------------------------------------------- style
PAGE, FRAME = '#f2eef7', '#808080'
TITLE_F, BAND_S, BLOCK = '#4f80bd', '#5b6b78', '#4874cc'
TXT = '#262626'
FONT = 'Microsoft YaHei,PingFang SC,Hiragino Sans GB,Helvetica'
FS = 16                      # single flat font size, as in the reference
LINE_H = 19          # measured from real draw.io renders at fontSize 16

PALETTE = {                  # per band: (box fill, box stroke, accent fill, chevron fill)
    1: ('#eef6fd', '#3b547f', '#b6d8f6', '#98d0ed'),
    2: ('#eef6fd', '#3b547f', '#b6d8f6', '#a2d2ea'),
    3: ('#fcead9', '#c08b5c', '#fddecd', '#f8d5b3'),
    4: ('#e5dfeb', '#9b979f', '#ccc2db', '#c8c1d9'),
    5: ('#dbeef4', '#668d89', '#bae2e4', '#d4eae4'),
}
EDGE = {1: '#1f3f6b', 2: '#1f3f6b', 3: '#7b5530', 4: '#7f5faf', 5: '#5f8484'}
TEAL_S = '#4f8f8b'

# ------------------------------------------------------------- geometry
CANVAS_W, CANVAS_H = 954, 1296
BAND_X, BAND_W = 124, 719
BANDS = {1: (75, 126), 2: (219, 294), 3: (530, 252), 4: (799, 204), 5: (1021, 234)}
CHEV_Y = {1: 94, 2: 322, 3: 599, 4: 855, 5: 1103}
RAIL_CY = {1: 138, 2: 366, 3: 656, 4: 901, 5: 1138}
FLOW_Y = [203, 514, 782, 1005]

problems = []
cells = []


# ------------------------------------------------------------- helpers
def esc(t):
    return html.escape(str(t), quote=True)


def text_w(line, fs=FS):
    """CJK/fullwidth glyphs occupy fs px; latin and spaces occupy fs/2."""
    w = 0.0
    for ch in line:
        w += fs if unicodedata.east_asian_width(ch) in ('W', 'F') else fs / 2
    return w


def fit(slot, lines, w, h, vertical=False):
    """Record a capacity problem if the text cannot fit the slot."""
    if vertical:
        need_h = len(lines) * LINE_H
        if need_h > h:
            problems.append(f'{slot}: 竖排 {len(lines)} 字需 {need_h}px，槽高仅 {h:g}px'
                            f'（最多 {int(h // LINE_H)} 字）')
        return
    usable = w - 8
    for ln in lines:
        if text_w(ln) > usable:
            problems.append(f'{slot}: "{ln}" 宽 {text_w(ln):.0f}px > 可用 {usable:.0f}px'
                            f'（约 {int(usable // FS)} 个汉字）')
    if len(lines) * LINE_H > h:
        problems.append(f'{slot}: {len(lines)} 行需 {len(lines) * LINE_H}px，槽高仅 {h:g}px'
                        f'（最多 {int(h // LINE_H)} 行）')


def lines_of(value):
    """Accept "a\\nb", ["a","b"] or "a" -> list of lines."""
    if value is None:
        return ['']
    if isinstance(value, (list, tuple)):
        return [str(v) for v in value]
    return str(value).split('\n')


def markup(lines):
    return '&lt;br&gt;'.join(esc(l) for l in lines)


def vert_markup(s):
    return '&lt;br&gt;'.join(esc(c) for c in str(s))


def add(cid, x, y, w, h, style, value=''):
    cells.append(
        f'        <mxCell id="{cid}" value="{value}" style="{style}" vertex="1" parent="1">\n'
        f'          <mxGeometry x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" as="geometry" />\n'
        f'        </mxCell>')


def edge(cid, pts, stroke, width=1.2, end='block', extra=''):
    (sx, sy), (tx, ty) = pts[0], pts[-1]
    style = (f'edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow={end};endFill=1;endSize=5;'
             f'strokeColor={stroke};strokeWidth={width};fontSize={FS};fontFamily={FONT};{extra}')
    way = ''
    if len(pts) > 2:
        way = ('\n            <Array as="points">\n' + '\n'.join(
            f'              <mxPoint x="{px:g}" y="{py:g}" />' for px, py in pts[1:-1]) +
            '\n            </Array>')
    cells.append(
        f'        <mxCell id="{cid}" value="" style="{style}" edge="1" parent="1">\n'
        f'          <mxGeometry relative="1" as="geometry">\n'
        f'            <mxPoint x="{sx:g}" y="{sy:g}" as="sourcePoint" />\n'
        f'            <mxPoint x="{tx:g}" y="{ty:g}" as="targetPoint" />{way}\n'
        f'          </mxGeometry>\n        </mxCell>')


def dashrect(cid, x, y, w, h, color, pattern='4 4'):
    edge(cid, [(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)],
         color, 1, 'none', f'dashed=1;dashPattern={pattern};')


def dashbox(cid, x, y, w, h, color, pattern='4 4'):
    """大虚线框落成真实顶点：无填充虚线框会被 check_layout 当容器豁免，
    框内元素不会被判重叠（小虚线框请改用闭合折线，见 preflight-rules.md）。"""
    add(cid, x, y, w, h, f'rounded=0;html=1;fillColor=none;strokeColor={color};'
                         f'strokeWidth=1;dashed=1;dashPattern={pattern};')


def box_style(fill, stroke, rounded=1, arc=8):
    return (f'rounded={rounded};arcSize={arc};whiteSpace=wrap;html=1;fillColor={fill};'
            f'strokeColor={stroke};strokeWidth=1;fontSize={FS};fontStyle=1;fontColor={TXT};'
            f'fontFamily={FONT};align=center;verticalAlign=middle;spacingLeft=2;spacingRight=2;')


LBL = (f'text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;'
       f'whiteSpace=wrap;fontSize={FS};fontStyle=1;fontColor={TXT};fontFamily={FONT};')


def slots(a, b, n, gap):
    """Split span [a,b] into n slots separated by `gap`; returns [(start, size)]."""
    size = (b - a - (n - 1) * gap) / n
    return [(a + i * (size + gap), size) for i in range(n)]


def tbox(cid, x, y, w, h, fill, stroke, value, rounded=1, arc=8):
    ls = lines_of(value)
    fit(cid, ls, w, h)
    add(cid, x, y, w, h, box_style(fill, stroke, rounded, arc), markup(ls))


def vbox(cid, x, y, w, h, fill, stroke, value, rounded=0):
    if w < FS + 6:
        problems.append(f'{cid}: 竖排槽宽 {w:g}px 不足（需 ≥ {FS + 6}px），请减少该组数量')
    fit(cid, list(str(value)), w, h, vertical=True)
    add(cid, x, y, w, h, box_style(fill, stroke, rounded), vert_markup(value))


def tlabel(cid, x, y, w, h, value):
    # transparent labels have no border, so a little vertical spill is harmless;
    # width is still strict because neighbours sit close on both sides
    ls = lines_of(value)
    fit(cid, ls, w, h * 1.4)
    add(cid, x, y, w, h, LBL, markup(ls))


def need(d, key, ctx):
    if key not in d:
        sys.exit(f'content 缺少字段: {ctx}.{key}')
    return d[key]


# ------------------------------------------------------------- bands
def build(c):
    # ---- page furniture -------------------------------------------------
    add('bg_left', 0, 0, 46, CANVAS_H, f'rounded=0;html=1;fillColor={PAGE};strokeColor=none;')
    add('bg_top', 46, 0, CANVAS_W - 46, 28, f'rounded=0;html=1;fillColor={PAGE};strokeColor=none;')

    title = lines_of(need(c, 'title', 'root'))
    fit('title', title, 719, 38)
    add('title', 124, 31, 719, 38,
        f'rounded=0;html=1;fillColor={TITLE_F};strokeColor={TITLE_F};fontSize={FS};fontStyle=1;'
        f'fontColor=#ffffff;fontFamily={FONT};align=center;verticalAlign=middle;whiteSpace=wrap;',
        markup(title))

    for b, (by, bh) in BANDS.items():
        add(f'band{b}', BAND_X, by, BAND_W, bh,
            f'rounded=0;html=1;fillColor=none;strokeColor={BAND_S};strokeWidth=1;'
            f'dashed=1;dashPattern=1 3;')

    rails = need(c, 'rails', 'root')
    if len(rails) != 5:
        sys.exit('rails 必须正好 5 项（每带一项）')
    lab_gaps = []
    for i, r in enumerate(rails, 1):
        cv = str(r['chevron'])
        fit(f'chev{i}', list(cv), 60, 92, vertical=True)
        add(f'chev{i}', 58, CHEV_Y[i], 60, 92,
            f'shape=singleArrow;direction=east;arrowWidth=1;arrowSize=0.22;html=1;'
            f'fillColor={PALETTE[i][3]};strokeColor=#5b93bd;strokeWidth=1;fontSize={FS};'
            f'fontStyle=1;fontColor={TXT};fontFamily={FONT};align=center;verticalAlign=middle;'
            f'spacingRight=10;', vert_markup(cv))
        txt = str(r['label'])
        h = len(txt) * 23
        y = RAIL_CY[i] - h // 2
        fit(f'rail{i}', list(txt), 26, h, vertical=True)
        add(f'rail{i}', 860, y, 26, h, LBL + 'fontColor=#3b547f;', vert_markup(txt))
        lab_gaps.append((y - 2, y + h + 2))

    # outer loop frame, interrupted where the title / chevrons / rails cover it
    edge('frame_t1', [(68, 49), (123, 49)], FRAME, 1, 'none')
    edge('frame_t2', [(844, 49), (874, 49)], FRAME, 1, 'none')
    edge('frame_b', [(68, 1273), (874, 1273)], FRAME, 1, 'none')

    def segs(y0, y1, gaps):
        out, cur = [], y0
        for g0, g1 in gaps:
            if g0 > cur:
                out.append((cur, g0))
            cur = max(cur, g1)
        if cur < y1:
            out.append((cur, y1))
        return out

    for i, (ya, yb) in enumerate(segs(49, 1273, [(y - 1, y + 93) for y in CHEV_Y.values()]), 1):
        edge(f'frame_l{i}', [(68, ya), (68, yb)], FRAME, 1, 'none')
    for i, (ya, yb) in enumerate(segs(49, 1273, lab_gaps), 1):
        edge(f'frame_r{i}', [(874, ya), (874, yb)], FRAME, 1, 'none')
    for i, ay in enumerate(FLOW_Y, 1):
        add(f'flow{i}', 470, ay, 30, 17,
            f'shape=singleArrow;direction=south;arrowWidth=0.62;arrowSize=0.5;html=1;'
            f'fillColor={BLOCK};strokeColor={BLOCK};')

    band1(c.get('band1', {}))
    band2(c.get('band2', {}))
    band3(c.get('band3', {}))
    band4(c.get('band4', {}))
    band5(c.get('band5', {}))


def band1(d):
    f, s, acc, _ = PALETTE[1]
    tbox('b1_head', 326, 87, 309, 34, acc, s, need(d, 'headline', 'band1'), rounded=0)
    items = need(d, 'items', 'band1')
    if not 2 <= len(items) <= 4:
        sys.exit('band1.items 需 2–4 项')
    for i, (x, w) in enumerate(slots(185, 779, len(items), 43), 1):
        tbox(f'b1_{i}', x, 157, w, 33, f, s, items[i - 1], rounded=0)
    centers = [x + w / 2 for x, w in slots(185, 779, len(items), 43)]
    edge('e1_stub', [(480, 122), (480, 138)], EDGE[1], end='none')
    edge('e1_bus', [(centers[0], 138), (centers[-1], 138)], EDGE[1], end='none')
    for i, cx in enumerate(centers, 1):
        edge(f'e1_d{i}', [(cx, 138), (cx, 156)], EDGE[1])


def band2(d):
    f, s, acc, _ = PALETTE[2]
    e = EDGE[2]
    src = need(d, 'sources', 'band2')
    if not 2 <= len(src) <= 4:
        sys.exit('band2.sources 需 2–4 项')
    sl = slots(136, 381, len(src), 11)
    for i, (x, w) in enumerate(sl, 1):
        tbox(f'b2_src{i}', x, 238, w, 48, f, s, src[i - 1])
    cx_all = [x + w / 2 for x, w in sl]
    mid = (136 + 381) / 2
    for i, cx in enumerate(cx_all, 1):
        if abs(cx - mid) > 1:
            edge(f'e2_s{i}', [(cx, 287), (cx, 305)], e, end='none')
    edge('e2_bus', [(cx_all[0], 305), (cx_all[-1], 305)], e, end='none')
    edge('e2_down', [(mid, 305), (mid, 317)], e)

    tbox('b2_prep', 211, 318, 95, 34, f, s, need(d, 'prep', 'band2'))
    tbox('b2_assume', 192, 383, 133, 64, f, s, need(d, 'assumptions', 'band2'))
    tbox('b2_symbol', 192, 471, 133, 33, f, s, need(d, 'symbols', 'band2'))
    edge('e2_p2a', [(258, 353), (258, 382)], e)
    edge('e2_a2s', [(258, 448), (258, 470)], e)

    vbox('b2_lv', 367, 396, 43, 104, acc, s, need(d, 'left_vertical', 'band2'))
    edge('e2_a2v', [(326, 415), (366, 415)], e)
    tbox('b2_c1', 401, 245, 155, 89, acc, s, need(d, 'content', 'band2'), rounded=0)
    edge('e2_c2f', [(478, 335), (478, 354)], e)

    DASH = 'dashed=1;dashPattern=4 4;'
    edge('sub_feat_t', [(417, 355), (539, 355)], '#3b6fbf', 1, 'none', DASH)
    edge('sub_feat_b', [(417, 503), (539, 503)], '#3b6fbf', 1, 'none', DASH)
    edge('sub_feat_l1', [(417, 355), (417, 436)], '#3b6fbf', 1, 'none', DASH)
    edge('sub_feat_l2', [(417, 460), (417, 503)], '#3b6fbf', 1, 'none', DASH)
    edge('sub_feat_r1', [(539, 355), (539, 436)], '#3b6fbf', 1, 'none', DASH)
    edge('sub_feat_r2', [(539, 460), (539, 503)], '#3b6fbf', 1, 'none', DASH)
    tlabel('b2_subtitle', 421, 358, 114, 24, need(d, 'subframe', 'band2'))
    dims = need(d, 'dims', 'band2')
    if not 2 <= len(dims) <= 4:
        sys.exit('band2.dims 需 2–4 项')
    for i, (y, h) in enumerate(slots(391, 494, len(dims), 10), 1):
        tbox(f'b2_dim{i}', 433, y, 93, h, '#ffffff', s, dims[i - 1], rounded=0)

    vbox('b2_rv', 548, 398, 43, 102, acc, s, need(d, 'right_vertical', 'band2'))
    edge('e2_hollowR', [(411, 448), (430, 448)], s, 2, 'block', 'endFill=0;endSize=14;')
    edge('e2_hollowL', [(547, 448), (528, 448)], s, 2, 'block', 'endFill=0;endSize=14;')

    dashbox('sub_six', 591, 235, 245, 155, '#3b6fbf')
    met = need(d, 'metrics', 'band2')
    if not 2 <= len(met) <= 4:
        sys.exit('band2.metrics 需 2–4 行')
    for i, (y, h) in enumerate(slots(248, 380, len(met), 8), 1):
        tbox(f'b2_ml{i}', 603, y, 64, h, f, s, met[i - 1][0], rounded=0)
        tbox(f'b2_mr{i}', 677, y, 147, h, f, s, met[i - 1][1], rounded=0)

    tbox('b2_agg', 650, 410, 126, 31, f, s, need(d, 'aggregator', 'band2'), rounded=0)
    tbox('b2_data', 604, 460, 220, 44, f, s, need(d, 'datasource', 'band2'), rounded=0)
    edge('e2_six2agg', [(713, 390), (713, 409)], e)
    edge('e2_data2agg', [(690, 459), (690, 442)], e)
    edge('e2_agg2rv', [(649, 425), (592, 425)], e)


def band3(d):
    f, s, acc, _ = PALETTE[3]
    e = EDGE[3]
    tbox('b3_top', 415, 542, 136, 35, f, s, need(d, 'top', 'band3'), arc=50)
    tbox('b3_bot', 414, 738, 136, 35, f, s, need(d, 'bottom', 'band3'), arc=50)
    left, right = need(d, 'left', 'band3'), need(d, 'right', 'band3')
    if not 2 <= len(left) <= 4 or not 2 <= len(right) <= 4:
        sys.exit('band3.left / band3.right 需各 2–4 项')
    rows_l = slots(600, 714, len(left), 12)
    rows_r = slots(600, 714, len(right), 12)
    for i, (y, h) in enumerate(rows_l, 1):
        tbox(f'b3_l{i}', 140, y, 144, h, f, s, left[i - 1])
    for i, (y, h) in enumerate(rows_r, 1):
        tbox(f'b3_r{i}', 677, y, 155, h, f, s, right[i - 1])
    vbox('b3_lv', 314, 587, 44, 140, f, s, need(d, 'left_vertical', 'band3'))
    vbox('b3_rv', 608, 587, 44, 140, f, s, need(d, 'right_vertical', 'band3'))
    tbox('b3_c2', 382, 604, 203, 105, acc, s, need(d, 'content', 'band3'), rounded=0)

    def bracket(tag, rows, x_box_edge, x_spine, x_target, sign):
        cys = [y + h / 2 for y, h in rows]
        for i, cy in enumerate(cys, 1):
            edge(f'{tag}_st{i}', [(x_box_edge, cy), (x_spine, cy)], e, end='none')
        edge(f'{tag}_spine', [(x_spine, cys[0]), (x_spine, cys[-1])], e, end='none')
        edge(f'{tag}_in', [(x_spine, 657), (x_target, 657)], e)

    bracket('e3_lb', rows_l, 285, 296, 313, 1)
    bracket('e3_rb', rows_r, 676, 665, 653, -1)
    edge('e3_l2c', [(359, 657), (381, 657)], e)
    edge('e3_r2c', [(607, 657), (586, 657)], e)
    edge('e3_top2l', [(414, 559), (336, 559), (336, 586)], e)
    edge('e3_top2r', [(552, 559), (630, 559), (630, 586)], e)
    edge('e3_l2bot', [(336, 728), (336, 755), (413, 755)], e)
    edge('e3_r2bot', [(630, 728), (630, 755), (551, 755)], e)


def band4(d):
    f, s, acc, _ = PALETTE[4]
    tf, ts, tacc = PALETTE[5][0], PALETTE[5][1], PALETTE[5][2]
    tbox('b4_banner', 136, 808, 697, 29, acc, '#8d84a8', need(d, 'banner', 'band4'), rounded=0)
    dashbox('sub_l', 134, 846, 307, 145, '#7f5faf')
    dashbox('sub_r', 527, 846, 307, 145, '#7f5faf')

    vbox('b4_lv', 153, 855, 41, 126, acc, '#8d84a8', need(d, 'left_vertical', 'band4'))
    li = need(d, 'left_items', 'band4')
    if not 3 <= len(li) <= 5:
        sys.exit('band4.left_items 需 3–5 项')
    for i, (y, h) in enumerate(slots(856, 981, len(li), 3), 1):
        tbox(f'b4_s{i}', 275, y, 147, h, f, s, li[i - 1], rounded=0)
    la = d.get('left_arrow_labels', ['', ''])
    edge('e4_l', [(196, 905), (272, 905)], EDGE[4])
    tlabel('b4_la1', 196, 878, 76, 22, la[0])
    tlabel('b4_la2', 196, 910, 76, 22, la[1] if len(la) > 1 else '')

    tlabel('b4_mid', 448, 845, 95, 55, need(d, 'middle', 'band4'))
    add('b4_double', 442, 894, 82, 23,
        'shape=doubleArrow;html=1;fillColor=#d9d9d9;strokeColor=#9a9a9a;strokeWidth=1;'
        'arrowWidth=0.4;arrowSize=0.28;')

    vbox('b4_rv', 547, 857, 36, 121, tacc, TEAL_S, need(d, 'right_vertical', 'band4'))
    ri = need(d, 'right_items', 'band4')
    if not 3 <= len(ri) <= 5:
        sys.exit('band4.right_items 需 3–5 项')
    for i, (y, h) in enumerate(slots(857, 978, len(ri), 3), 1):
        tbox(f'b4_v{i}', 650, y, 89, h, tf, ts, ri[i - 1], rounded=0)
    ra = d.get('right_arrow_labels', ['', ''])
    edge('e4_r', [(584, 905), (648, 905)], TEAL_S)
    tlabel('b4_ra1', 584, 878, 64, 22, ra[0])
    tlabel('b4_ra2', 584, 910, 64, 22, ra[1] if len(ra) > 1 else '')

    spans = need(d, 'right_spans', 'band4')
    if not 1 <= len(spans) <= 3:
        sys.exit('band4.right_spans 需 1–3 项')
    for i, (y, h) in enumerate(slots(857, 979, len(spans), 3), 1):
        tbox(f'b4_o{i}', 742, y, 76, h, tf, ts, spans[i - 1], rounded=0)


def band5(d):
    f, s, acc, _ = PALETTE[5]
    e = EDGE[5]
    pu, pus, puacc = PALETTE[4][0], PALETTE[4][1], PALETTE[4][2]
    li = need(d, 'left_items', 'band5')
    if not 3 <= len(li) <= 5:
        sys.exit('band5.left_items 需 3–5 项')
    for i, (y, h) in enumerate(slots(1030, 1188, len(li), 9), 1):
        tbox(f'b5_p{i}', 140, y, 100, h, pu, pus, li[i - 1])
    tbox('b5_corner', 138, 1199, 104, 53, puacc, '#8d84a8', need(d, 'corner', 'band5'), arc=25)
    tbox('b5_pill', 262, 1215, 184, 37, puacc, '#8d84a8', need(d, 'pill', 'band5'), arc=50)

    dashrect('sub_cycle', 259, 1030, 190, 158, '#4f8fbf', '1 3')
    cyc = need(d, 'cycle', 'band5')
    if len(cyc) != 3:
        sys.exit('band5.cycle 必须正好 3 项（三元循环）')
    tlabel('b5_cy1', 272, 1080, 72, 22, cyc[0])
    tlabel('b5_cy2', 370, 1080, 72, 22, cyc[1])
    tlabel('b5_cy3', 326, 1158, 72, 22, cyc[2])
    CY = dict(width=9, end='block', extra='edgeStyle=none;curved=1;endSize=2;')
    edge('ic_cyc1', [(330, 1068), (348, 1040), (386, 1050)], '#ccccd6', **CY)
    edge('ic_cyc2', [(276, 1106), (288, 1142), (326, 1152)], '#ccccd6', **CY)
    edge('ic_cyc3', [(392, 1152), (432, 1140), (436, 1104)], '#ccccd6', **CY)
    edge('e5_pill2cyc', [(354, 1214), (354, 1190)], EDGE[4])

    tbox('b5_c4', 462, 1039, 139, 107, acc, TEAL_S, need(d, 'content', 'band5'), rounded=0)
    hexl = lines_of(need(d, 'hex', 'band5'))
    fit('b5_hex', hexl, 57, 59)
    add('b5_hex', 623, 1061, 57, 59,
        f'shape=hexagon;perimeter=hexagonPerimeter2;html=1;fixedSize=1;size=12;fillColor={acc};'
        f'strokeColor={TEAL_S};strokeWidth=1;fontSize={FS};fontStyle=1;fontColor={TXT};'
        f'fontFamily={FONT};whiteSpace=wrap;align=center;verticalAlign=middle;', markup(hexl))
    tbox('b5_eval', 716, 1031, 86, 31, f, s, need(d, 'eval', 'band5'), rounded=0)
    edge('e5_eval2hex', [(715, 1046), (651, 1046), (651, 1060)], e)
    edge('e5_hex2c', [(622, 1090), (602, 1090)], e)

    met = need(d, 'metrics', 'band5')
    if not 2 <= len(met) <= 5:
        sys.exit('band5.metrics 需 2–5 项')
    cols = slots(689, 829, len(met), 7)
    for i, (x, w) in enumerate(cols, 1):
        vbox(f'b5_m{i}', x, 1109, w, 124, f, s, met[i - 1], rounded=1)
    edge('e5_evd', [(759, 1063), (759, 1085)], e, end='none')
    edge('e5_evbus', [(cols[0][0] + cols[0][1] / 2, 1085),
                      (cols[-1][0] + cols[-1][1] / 2, 1085)], e, end='none')
    for i, (x, w) in enumerate(cols, 1):
        edge(f'e5_m{i}', [(x + w / 2, 1085), (x + w / 2, 1108)], e)

    cases = need(d, 'cases', 'band5')
    if not 1 <= len(cases) <= 3:
        sys.exit('band5.cases 需 1–3 项')
    # the case frame is bottom-anchored at y=1242 and grows upward with the item count,
    # so 3 items still get a legible 23px row instead of being squeezed into 14px
    bh, gp = (26, 8) if len(cases) <= 2 else (23, 6)
    inner = len(cases) * bh + (len(cases) - 1) * gp
    top = 1233 - inner
    add('sub_case_bg', 560, top - 4, 109, inner + 8,
        'rounded=0;html=1;fillColor=#fdf7ec;strokeColor=none;')
    dashrect('sub_case', 559, top - 5, 111, inner + 10, '#d09a50')
    for i in range(len(cases)):
        tbox(f'b5_case{i + 1}', 567, top + i * (bh + gp), 96, bh,
             PALETTE[3][0], PALETTE[3][1], cases[i], arc=30)
    edge('e5_case2c', [(556, 1205), (556, 1147)], e)


# ------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description='Render a 5-band research roadmap .drawio')
    ap.add_argument('content', help='content JSON path')
    ap.add_argument('-o', '--out', default=None, help='output .drawio path')
    ap.add_argument('--check', action='store_true', help='only run the capacity check')
    a = ap.parse_args()

    c = json.loads(pathlib.Path(a.content).read_text(encoding='utf-8'))
    build(c)

    if problems:
        print(f'[FAIL] 容量检查未通过（{len(problems)} 处超框）：', file=sys.stderr)
        for p in problems:
            print(f'  - {p}', file=sys.stderr)
        print('\n请缩短文案或改用多行（"\\n" 断行），再重新渲染。', file=sys.stderr)
        sys.exit(2)
    print('[OK] 容量检查通过')
    if a.check:
        return

    out = pathlib.Path(a.out or pathlib.Path(a.content).with_suffix('.drawio'))
    xml = ('<mxfile host="app.diagrams.net" agent="claude-code" version="24.7.17" pages="1">\n'
           '  <diagram id="research-roadmap" name="技术路线图">\n'
           f'    <mxGraphModel dx="{CANVAS_W}" dy="{CANVAS_H}" grid="0" gridSize="10" guides="1" '
           'tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" '
           f'pageWidth="{CANVAS_W}" pageHeight="{CANVAS_H}" math="0" shadow="0">\n'
           '      <root>\n        <mxCell id="0" />\n        <mxCell id="1" parent="0" />\n'
           + '\n'.join(cells) +
           '\n      </root>\n    </mxGraphModel>\n  </diagram>\n</mxfile>\n')
    out.write_text(xml, encoding='utf-8')
    print(f'[OK] 已写出 {out}（{len(cells)} 个图元）')


if __name__ == '__main__':
    main()
