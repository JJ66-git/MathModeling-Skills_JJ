#!/usr/bin/env python3
"""framework-3col：三栏式研究框架图（左阶段链 / 中研究内容 / 右研究方法）。

    python3 framework_3col.py content.json -o out.drawio
    python3 framework_3col.py content.json --check

画布宽 1026 固定，高度按内容自动生长。中栏每个内容块由若干"版式段"拼成，
段类型见 references/framework-3col.md。写文件前逐槽做中文字宽校验。
"""
import argparse
import html
import json
import pathlib
import sys
import unicodedata

W = 1026
FS, FS_T = 15, 16          # 正文 / 标题
LINE_H = 19
FONT = 'Microsoft YaHei,PingFang SC,Hiragino Sans GB,Helvetica'
INK = '#262626'

PINK, PINK_S = '#f8b8d8', '#d2679f'
GTITLE, GTITLE_S = '#d3f7d1', '#2f4f2f'
GSUB, GSUB_S = '#b0e898', '#4a7a3a'
PURPLE, PURPLE_S = '#d8b8f8', '#8a5cc0'
YELLOW, YELLOW_S = '#f8e0b8', '#c89a4a'
PEACH, PEACH_S = '#f8d8c0', '#c98a63'
BLUE, BLUE_S = '#c0c8f8', '#6a74c0'
MAGENTA, MAGENTA_S = '#f0c0f8', '#b060c0'
GREEN, GREEN_S = '#b0f0b8', '#4a9a55'
SALMON, SALMON_S = '#f8c8c0', '#cc7a6a'
TEAL, TEAL_2 = '#85bbb4', '#cfe8e4'
SKY, SKY_2 = '#c6edfd', '#e8f7ff'
METHOD, METHOD_S = '#90c898', '#4f8a58'
GREY, GREY_2 = '#8e8e8e', '#d8d8d8'
LINE = '#1a1a1a'
FILLS = {'yellow': (YELLOW, YELLOW_S), 'peach': (PEACH, PEACH_S), 'blue': (BLUE, BLUE_S),
         'green': (GREEN, GREEN_S), 'magenta': (MAGENTA, MAGENTA_S), 'purple': (PURPLE, PURPLE_S),
         'salmon': (SALMON, SALMON_S)}

RAIL_L, RAIL_R = (32, 142), (874, 1020)     # 左右栏的 x 范围
MID = (181, 852)                            # 中栏虚线容器 x 范围
cells, problems = [], []


def esc(t):
    return html.escape(str(t), quote=True)


def tw(line, fs=FS):
    return sum(fs if unicodedata.east_asian_width(c) in ('W', 'F') else fs / 2 for c in line)


def lines_of(v):
    if v is None:
        return ['']
    return [str(x) for x in v] if isinstance(v, (list, tuple)) else str(v).split('\n')


def fit(cid, ls, w, h, fs=FS, soft=1.0):
    for ln in ls:
        usable = w - (8 if len(ln) > 1 else 2)
        if tw(ln, fs) > usable:
            problems.append(f'{cid}: "{ln}" 宽 {tw(ln, fs):.0f}px > 可用 {usable:.0f}px'
                            f'（约 {int(usable // fs)} 个汉字）')
    if len(ls) * (fs + 3) > h * soft:
        problems.append(f'{cid}: {len(ls)} 行需 {len(ls) * (fs + 3)}px，槽高仅 {h:g}px')


def mk(lines):
    return '&lt;br&gt;'.join(esc(l) for l in lines)


def raw(cid, x, y, w, h, style, val=''):
    cells.append(f'        <mxCell id="{cid}" value="{val}" style="{style}" vertex="1" parent="1">\n'
                 f'          <mxGeometry x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}"'
                 f' as="geometry" />\n        </mxCell>')


def box(cid, x, y, w, h, text, fill, stroke, fs=FS, arc=10, extra=''):
    ls = lines_of(text)
    fit(cid, ls, w, h, fs)
    raw(cid, x, y, w, h,
        f'rounded=1;arcSize={arc};whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};'
        f'strokeWidth=1;fontSize={fs};fontStyle=1;fontColor={INK};fontFamily={FONT};'
        f'align=center;verticalAlign=middle;spacingLeft=2;spacingRight=2;{extra}', mk(ls))


def vtext(cid, x, y, w, h, text, fill, stroke, fs=FS):
    chars = list(str(text))
    need = len(chars) * (fs + 3)
    if need > h:
        problems.append(f'{cid}: 竖排 {len(chars)} 字需 {need}px > 槽高 {h:g}px')
    raw(cid, x, y, w, h,
        f'rounded=1;arcSize=12;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};'
        f'strokeWidth=1;fontSize={fs};fontStyle=1;fontColor={INK};fontFamily={FONT};'
        f'align=center;verticalAlign=middle;', '&lt;br&gt;'.join(esc(c) for c in chars))


def edge(cid, pts, stroke=LINE, width=1.6, end='block', extra=''):
    (sx, sy), (tx, ty) = pts[0], pts[-1]
    way = ''
    if len(pts) > 2:
        way = ('\n            <Array as="points">\n' + '\n'.join(
            f'              <mxPoint x="{px:g}" y="{py:g}" />' for px, py in pts[1:-1]) +
            '\n            </Array>')
    cells.append(
        f'        <mxCell id="{cid}" value="" style="edgeStyle=orthogonalEdgeStyle;rounded=0;'
        f'html=1;endArrow={end};endFill=1;endSize=5;strokeColor={stroke};strokeWidth={width};'
        f'{extra}" edge="1" parent="1">\n          <mxGeometry relative="1" as="geometry">\n'
        f'            <mxPoint x="{sx:g}" y="{sy:g}" as="sourcePoint" />\n'
        f'            <mxPoint x="{tx:g}" y="{ty:g}" as="targetPoint" />{way}\n'
        f'          </mxGeometry>\n        </mxCell>')


def dashframe(cid, x, y, w, h, color='#1a1a1a', pattern='6 5'):
    if w > 200 and h > 100:
        raw(cid, x, y, w, h, f'rounded=0;html=1;fillColor=none;strokeColor={color};'
                             f'strokeWidth=1.4;dashed=1;dashPattern={pattern};')
    else:
        edge(cid, [(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)], color, 1.4, 'none',
             f'dashed=1;dashPattern={pattern};')


def block_arrow(cid, x, y, w, h, direction, fill, grad=None):
    g = f'gradientColor={grad};gradientDirection={"east" if direction in ("east","west") else "south"};' if grad else ''
    raw(cid, x, y, w, h,
        f'shape=singleArrow;direction={direction};arrowWidth=0.62;arrowSize=0.34;html=1;'
        f'fillColor={fill};strokeColor=none;{g}')


def slots(a, b, n, gap):
    size = (b - a - (n - 1) * gap) / n
    return [(a + i * (size + gap), size) for i in range(n)]


# ---------------------------------------------------------------- 版式段
def sec_height(s):
    t = s['type']
    if t == 'columns':
        def col_h(c):
            return sum(30 + (len(lines_of(i)) - 1) * 20 + 8 for i in c['items'])
        return 52 + max(col_h(c) for c in s['columns']) + 4
    if t == 'chain':
        return 60
    if t == 'converge':
        need = max(max(len(str(o)) * 14 + 10 for o in g['outs']) for g in s['groups'])
        return max(44 + max(len(g['items']) for g in s['groups']) * 45, 44 + need + 20)
    if t == 'mechanism':
        return max(len(s['left']), len(s['right'])) * 40 + 44
    if t == 'pair':
        return 44 + max(len(s['left']['items']), len(s['right']['rows'])) * 37 + 10
    sys.exit(f'未知段类型 {t}')


def draw_section(k, s, x0, x1, y):
    t, h = s['type'], sec_height(s)

    if t == 'columns':
        cols = s['columns']
        for i, (cx, cw) in enumerate(slots(x0 + 12, x1 - 12, len(cols), 60)):
            c = cols[i]
            dashframe(f's{k}_f{i}', cx - 10, y, cw + 20, h, pattern='4 4')
            box(f's{k}_h{i}', cx, y + 10, cw, 34, c['header'], PURPLE, PURPLE_S)
            iy = y + 52
            for j, it in enumerate(c['items']):
                ih = 30 + (len(lines_of(it)) - 1) * 20     # 多行项要长高，否则会压到下一项
                box(f's{k}_i{i}_{j}', cx, iy, cw, ih, it, YELLOW, YELLOW_S)
                iy += ih + 8
            if i:
                px = cx - 10 - 40
                block_arrow(f's{k}_a{i}', px, y + 16, 34, 24, 'east', '#f79a8a')
        return h

    if t == 'chain':
        items = s['items']
        for i, (cx, cw) in enumerate(slots(x0 + 20, x1 - 20, len(items), 66)):
            box(f's{k}_c{i}', cx, y + 6, cw, 48, items[i], YELLOW, YELLOW_S)
            if i:
                edge(f's{k}_ce{i}', [(cx - 62, y + 30), (cx - 4, y + 30)], '#3cb878', 4)
        return h

    if t == 'converge':
        for gi, (gx, gw) in enumerate(slots(x0 + 12, x1 - 12, len(s['groups']), 26)):
            g = s['groups'][gi]
            dashframe(f's{k}_gf{gi}', gx - 8, y, gw + 16, h, pattern='4 4')
            box(f's{k}_gh{gi}', gx + gw * 0.10, y + 8, gw * 0.80, 32, g['header'], GSUB, GSUB_S)
            n = len(g['items'])
            iw = gw * 0.52
            for j, it in enumerate(g['items']):
                box(f's{k}_gi{gi}_{j}', gx, y + 50 + j * 45, iw, 34, it, PEACH, PEACH_S)
            cys = [y + 50 + j * 45 + 17 for j in range(n)]
            spine = gx + iw + 14
            for j, cy in enumerate(cys):
                edge(f's{k}_gb{gi}_{j}', [(gx + iw + 1, cy), (spine, cy)], LINE, 1.6, 'none')
            edge(f's{k}_gs{gi}', [(spine, cys[0]), (spine, cys[-1])], LINE, 1.6, 'none')
            mid = (cys[0] + cys[-1]) / 2
            outs = g['outs']
            ow = (gw - iw - 30) / len(outs) - 8
            for j, o in enumerate(outs):
                ox = spine + 16 + j * (ow + 26)
                oh = max(len(str(o)) * 14 + 10, 60)          # 竖排按字数长高
                oy = mid - oh / 2
                vtext(f's{k}_go{gi}_{j}', ox, oy, ow, oh, o, PEACH, PEACH_S, fs=11)
                edge(f's{k}_goe{gi}_{j}', [(ox - 15, mid), (ox - 1, mid)], LINE, 1.6)
        return h

    if t == 'mechanism':
        dashframe(f's{k}_f', x0 + 8, y, x1 - x0 - 16, h, pattern='4 4')
        n_l, n_r = len(s['left']), len(s['right'])
        lw, rw = 150, 155
        lx, rx = x0 + 26, x1 - 26 - rw
        for j, it in enumerate(s['left']):
            box(f's{k}_l{j}', lx, y + 12 + j * 40, lw, 32, it, BLUE, BLUE_S)
        for j, it in enumerate(s['right']):
            box(f's{k}_r{j}', rx, y + 12 + j * 40, rw, 32, it, BLUE, BLUE_S)
        lcy = [y + 28 + j * 40 for j in range(n_l)]
        rcy = [y + 28 + j * 40 for j in range(n_r)]
        mid_y = y + 12 + max(n_l, n_r) * 40 / 2
        for j, cy in enumerate(lcy):
            edge(f's{k}_lb{j}', [(lx + lw + 1, cy), (lx + lw + 20, cy)], LINE, 1.6, 'none')
        edge(f's{k}_ls', [(lx + lw + 20, lcy[0]), (lx + lw + 20, lcy[-1])], LINE, 1.6, 'none')
        for j, cy in enumerate(rcy):
            edge(f's{k}_rb{j}', [(rx - 1, cy), (rx - 20, cy)], LINE, 1.6, 'none')
        edge(f's{k}_rs', [(rx - 20, rcy[0]), (rx - 20, rcy[-1])], LINE, 1.6, 'none')
        vx, vw = lx + lw + 36, 34
        vtext(f's{k}_lv', vx, mid_y - 45, vw, 90, s['left_label'], MAGENTA, MAGENTA_S)
        vx2 = rx - 20 - 16 - vw
        vtext(f's{k}_rv', vx2, mid_y - 45, vw, 90, s['right_label'], MAGENTA, MAGENTA_S)
        cw = vx2 - (vx + vw) - 60
        cx = vx + vw + 30
        box(f's{k}_c', cx, mid_y - 32, cw, 64, s['center'], MAGENTA, MAGENTA_S)
        edge(f's{k}_e1', [(lx + lw + 21, mid_y), (vx - 1, mid_y)], LINE, 1.6)
        edge(f's{k}_e2', [(vx + vw + 1, mid_y), (cx - 1, mid_y)], LINE, 1.6)
        edge(f's{k}_e3', [(vx2 - 1, mid_y), (cx + cw + 1, mid_y)], LINE, 1.6)
        edge(f's{k}_e4', [(rx - 21, mid_y), (vx2 + vw + 1, mid_y)], LINE, 1.6)
        bw = 220
        box(f's{k}_b', cx + cw / 2 - bw / 2, y + h - 40, bw, 32, s['bottom'], MAGENTA, MAGENTA_S)
        edge(f's{k}_e5', [(cx + cw / 2, mid_y + 33), (cx + cw / 2, y + h - 41)], LINE, 1.6)
        return h

    if t == 'pair':
        L, R = s['left'], s['right']
        lw = (x1 - x0) * 0.35
        lx = x0 + 16
        rx = x0 + 16 + lw + 58
        rw = x1 - 16 - rx
        raw(f's{k}_lbg', lx - 8, y, lw + 16, h, 'rounded=0;html=1;fillColor=#eef6ff;strokeColor=none;')
        raw(f's{k}_rbg', rx - 8, y, rw + 16, h, 'rounded=0;html=1;fillColor=#eef6ff;strokeColor=none;')
        dashframe(f's{k}_lf', lx - 8, y, lw + 16, h, pattern='4 4')
        dashframe(f's{k}_rf', rx - 8, y, rw + 16, h, pattern='4 4')
        box(f's{k}_lh', lx + 6, y + 8, lw - 12, 32, L['header'], SALMON, SALMON_S)
        for j, it in enumerate(L['items']):
            box(f's{k}_li{j}', lx + 16, y + 50 + j * 37, lw - 32, 30, it, GREEN, GREEN_S)
        box(f's{k}_rh', rx + 6, y + 8, rw - 12, 32, R['header'], SALMON, SALMON_S)
        for j, row in enumerate(R['rows']):
            for i, (cx, cw) in enumerate(slots(rx + 6, rx + rw - 6, len(row), 10)):
                box(f's{k}_ri{j}_{i}', cx, y + 50 + j * 37, cw, 30, row[i], GREEN, GREEN_S)
        edge(f's{k}_pe', [(lx + lw + 12, y + h / 2), (rx - 14, y + h / 2)], '#9a8cf0', 4)
        return h


# ---------------------------------------------------------------- 主体
def build(c):
    heads = c.get('headers', ['研究框架', '研究内容', '研究方法'])
    blocks = c['blocks']
    stages = c['stages']
    methods = c['methods']

    # 中栏：块高 = 标题 + 各段 + 间隙
    GAP_IN, GAP_BLK, TOP = 14, 16, 118
    hs = []
    for b in blocks:
        secs = [sec_height(s) for s in b['sections']]
        hs.append(22 + 41 + GAP_IN + sum(secs) + (len(secs) - 1) * GAP_IN + 14)
    total = TOP + sum(hs) + GAP_BLK * (len(blocks) - 1) + 12
    H = max(total, 400)

    for i, t in enumerate(heads):
        x = [18, 432, 880][i]
        box(f'hd{i}', x, 47, 147, 48, t, PINK, PINK_S, FS_T, arc=20)

    y = TOP
    for bi, b in enumerate(blocks):
        h = hs[bi]
        dashframe(f'blk{bi}', MID[0], y, MID[1] - MID[0], h)
        box(f'blk{bi}_t', MID[0] + 85, y + 22, MID[1] - MID[0] - 170, 41,
            b['title'], GTITLE, GTITLE_S, FS_T, arc=12)
        yy = y + 22 + 41 + GAP_IN
        for si, s in enumerate(b['sections']):
            yy += draw_section(f'{bi}{si}', s, MID[0], MID[1], yy) + GAP_IN
        y += h + GAP_BLK

    # 左栏：阶段旗标按块对齐，块间用灰渐变箭头
    tops = []
    y = TOP
    for bi in range(len(blocks)):
        tops.append((y, hs[bi]))
        y += hs[bi] + GAP_BLK
    n = len(stages)
    step = (tops[-1][0] + tops[-1][1] - TOP) / n
    ys = []
    for i, st in enumerate(stages):
        if 'block' in st:                       # 对齐到某个内容块内的相对位置
            bt, bh = tops[min(st['block'], len(tops) - 1)]
            ys.append(bt + st.get('at', 0.5) * bh - 41)
        else:                                   # 未指定则等距
            ys.append(TOP + 77 + i * step)
    block_arrow('rail_a0', 78, 110, 18, max(ys[0] - 122, 20), 'south', GREY, GREY_2)
    for i, st in enumerate(stages):
        sy = ys[i]
        fill, grad = (TEAL, TEAL_2) if st.get('tone', 'teal') == 'teal' else (SKY, SKY_2)
        # 宽度止于中栏容器左边，避免箭头尖伸进内容区压住盒子
        raw(f'st{i}', RAIL_L[0], sy, MID[0] - RAIL_L[0] - 2, 82,
            f'shape=singleArrow;direction=east;arrowWidth=0.66;arrowSize=0.42;html=1;'
            f'fillColor={fill};gradientColor={grad};gradientDirection=east;strokeColor=none;'
            f'fontSize={FS_T};fontStyle=1;fontColor={INK};fontFamily={FONT};whiteSpace=wrap;'
            f'align=left;verticalAlign=middle;spacingLeft=14;', mk(lines_of(st['text'])))
        if i + 1 < n:
            gap = ys[i + 1] - (sy + 82)
            if gap > 24:
                block_arrow(f'rail_a{i+1}', 78, sy + 92, 18, gap - 20, 'south', GREY, GREY_2)

    # 右栏：方法组等距分布，组间灰渐变箭头
    m = len(methods)
    mstep = (tops[-1][0] + tops[-1][1] - TOP) / m
    mys, mhs = [], []
    for i, mt in enumerate(methods):
        txt = mt['text'] if isinstance(mt, dict) else mt
        mh = max(100, len(lines_of(txt)) * 19 + 16)
        if isinstance(mt, dict) and 'block' in mt:
            bt, bh = tops[min(mt['block'], len(tops) - 1)]
            mys.append(bt + mt.get('at', 0.5) * bh - mh / 2)
        else:
            mys.append(TOP + 67 + i * mstep)
        mhs.append(mh)
    block_arrow('mrail_a0', 938, 100, 22, max(mys[0] - 112, 20), 'south', GREY, GREY_2)
    for i, mt in enumerate(methods):
        txt = mt['text'] if isinstance(mt, dict) else mt
        box(f'mt{i}', RAIL_R[0], mys[i], RAIL_R[1] - RAIL_R[0], mhs[i], txt,
            METHOD, METHOD_S, FS, arc=4)
        if i + 1 < m:
            gap = mys[i + 1] - (mys[i] + mhs[i])
            if gap > 24:
                block_arrow(f'mrail_a{i+1}', 938, mys[i] + mhs[i] + 10, 22, gap - 20,
                            'south', GREY, GREY_2)
    return int(H)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('content')
    ap.add_argument('-o', '--out')
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    c = json.loads(pathlib.Path(a.content).read_text(encoding='utf-8'))
    H = build(c)
    if problems:
        print(f'[FAIL] 容量检查未通过（{len(problems)} 处）：', file=sys.stderr)
        for p in problems:
            print('  - ' + p, file=sys.stderr)
        sys.exit(2)
    print(f'[OK] 容量检查通过（画布 {W}×{H}）')
    if a.check:
        return
    out = pathlib.Path(a.out or pathlib.Path(a.content).with_suffix('.drawio'))
    out.write_text(
        '<mxfile host="app.diagrams.net" agent="claude-code" version="24.7.17" pages="1">\n'
        '  <diagram id="framework" name="研究框架">\n'
        f'    <mxGraphModel dx="{W}" dy="{H}" grid="0" gridSize="10" guides="1" tooltips="1" '
        f'connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{W}" pageHeight="{H}" '
        'math="0" shadow="0">\n      <root>\n        <mxCell id="0" />\n'
        '        <mxCell id="1" parent="0" />\n' + '\n'.join(cells) +
        '\n      </root>\n    </mxGraphModel>\n  </diagram>\n</mxfile>\n', encoding='utf-8')
    print(f'[OK] 已写出 {out}（{len(cells)} 个图元）')


if __name__ == '__main__':
    main()
