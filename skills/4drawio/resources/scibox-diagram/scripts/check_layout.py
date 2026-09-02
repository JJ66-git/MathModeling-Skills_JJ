#!/usr/bin/env python3
"""check_layout.py — 对任意 .drawio 做版式体检（针对中文示意图调校）。

    python3 check_layout.py fig.drawio            # 体检
    python3 check_layout.py fig.drawio --strict   # WARN 也算失败

FAIL：文字溢出、元素越界、id 重复、盒子重叠、连线穿盒、内嵌位图。
WARN：端点压在盒边、疑似空盒、字号种类过多、填充色发散。

用中文字宽模型（全角=字号、半角=字号/2、行高=字号+3）；**不**对紧密堆叠的行列间距报警——
学术示意图里 3px 贴合的表格式堆叠是刻意的，不是缺陷。规则详解见 references/preflight-rules.md。
"""
import argparse
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET

FAIL, WARN = [], []


def style_of(s):
    d = {}
    for kv in (s or '').split(';'):
        if '=' in kv:
            k, v = kv.split('=', 1)
            d[k.strip()] = v.strip()
        elif kv.strip():
            d[kv.strip()] = '1'
    return d


def text_w(line, fs):
    return sum(fs if unicodedata.east_asian_width(c) in ('W', 'F') else fs / 2 for c in line)


def plain(v):
    v = re.sub(r'<br\s*/?>', '\n', v or '', flags=re.I)
    v = re.sub(r'<[^>]+>', '', v)
    return v.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"')


def seg_rect(x1, y1, x2, y2, r):
    """线段与矩形是否相交（含边界接触）。"""
    rx, ry, rw, rh = r
    if max(x1, x2) < rx or min(x1, x2) > rx + rw or max(y1, y2) < ry or min(y1, y2) > ry + rh:
        return False
    if x1 == x2 or y1 == y2:                     # 正交线段：包围盒相交即相交
        return True
    for ax, ay, bx, by in ((rx, ry, rx + rw, ry), (rx, ry + rh, rx + rw, ry + rh),
                           (rx, ry, rx, ry + rh), (rx + rw, ry, rx + rw, ry + rh)):
        d1 = (x2 - x1) * (ay - y1) - (y2 - y1) * (ax - x1)
        d2 = (x2 - x1) * (by - y1) - (y2 - y1) * (bx - x1)
        d3 = (bx - ax) * (y1 - ay) - (by - ay) * (x1 - ax)
        d4 = (bx - ax) * (y2 - ay) - (by - ay) * (x2 - ax)
        if ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0)):
            return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('drawio')
    ap.add_argument('--strict', action='store_true')
    a = ap.parse_args()

    root = ET.parse(a.drawio).getroot()
    model = root.iter('mxGraphModel').__next__()
    pw, ph = float(model.get('pageWidth', 0) or 0), float(model.get('pageHeight', 0) or 0)

    boxes, edges, ids = [], [], {}
    for c in root.iter('mxCell'):
        cid = c.get('id')
        if cid in ids:
            FAIL.append(f'id 重复: {cid}')
        ids[cid] = 1
        st = style_of(c.get('style'))
        g = c.find('mxGeometry')
        if c.get('vertex') == '1' and g is not None:
            x, y = float(g.get('x', 0)), float(g.get('y', 0))
            w, h = float(g.get('width', 0)), float(g.get('height', 0))
            fs = float(st.get('fontSize', 12))
            txt = plain(c.get('value'))
            raw_style = c.get('style') or ''
            if 'data:image/png' in raw_style or 'data:image/jpeg' in raw_style:
                FAIL.append(f'{cid}: 内嵌位图（要求可编辑时整块不可再改）')
            is_text = st.get('strokeColor') == 'none' or st.get('style', '').startswith('text')
            is_frame = st.get('dashed') == '1' and st.get('fillColor') == 'none'
            is_shape = 'shape=' in raw_style
            boxes.append(dict(id=cid, r=(x, y, w, h), fs=fs, txt=txt, st=st, shape=is_shape,
                              fill=st.get('fillColor'), solid=not (is_text or is_frame)))
            if (not txt.strip() and not is_text and not is_frame and not is_shape
                    and st.get('fillColor') not in (None, 'none')):
                WARN.append(f'{cid}: 有填充有描边却没有文字，疑似漏填')
            if pw and (x < -1 or y < -1 or x + w > pw + 1 or y + h > ph + 1):
                FAIL.append(f'{cid}: 越出画布 ({x:g},{y:g} {w:g}×{h:g})')
            if txt.strip() and w and h and 'shape=singleArrow' not in (c.get('style') or ''):
                lines = txt.split('\n')
                for ln in lines:
                    # 单字居中时边距极小（竖排堆叠常见），多字才按两侧各 4px 估
                    usable = w - (8 if len(ln) > 1 else 2)
                    if text_w(ln, fs) > usable:
                        FAIL.append(f'{cid}: 文字溢出 "{ln[:18]}" 需 {text_w(ln, fs):.0f}px'
                                    f' > 可用 {usable:.0f}px')
                        break
                if len(lines) * (fs + 3) > h * (1.4 if is_text else 1.0):
                    FAIL.append(f'{cid}: {len(lines)} 行放不下（槽高 {h:g}px）')
        elif c.get('edge') == '1' and g is not None:
            pts = []
            sp, tp = g.find("mxPoint[@as='sourcePoint']"), g.find("mxPoint[@as='targetPoint']")
            arr = g.find("Array[@as='points']")
            if sp is not None:
                pts.append((float(sp.get('x')), float(sp.get('y'))))
            if arr is not None:
                pts += [(float(p.get('x')), float(p.get('y'))) for p in arr]
            if tp is not None:
                pts.append((float(tp.get('x')), float(tp.get('y'))))
            if len(pts) >= 2:
                edges.append((cid, pts))

    solid = [b for b in boxes if b['solid']]
    for i in range(len(solid)):
        for j in range(i + 1, len(solid)):
            (x1, y1, w1, h1), (x2, y2, w2, h2) = solid[i]['r'], solid[j]['r']
            if x1 < x2 + w2 and x2 < x1 + w1 and y1 < y2 + h2 and y2 < y1 + h1:
                FAIL.append(f"{solid[i]['id']} 与 {solid[j]['id']} 重叠")

    for cid, pts in edges:
        for k in range(len(pts) - 1):
            x1, y1 = pts[k]
            x2, y2 = pts[k + 1]
            for b in solid:
                bx, by, bw, bh = b['r']
                on_border = (abs(x1 - bx) < 0.6 or abs(x1 - bx - bw) < 0.6 or
                             abs(y1 - by) < 0.6 or abs(y1 - by - bh) < 0.6)
                ends_here = (k == 0 and bx - 0.6 <= x1 <= bx + bw + 0.6
                             and by - 0.6 <= y1 <= by + bh + 0.6)
                if ends_here and on_border:
                    WARN.append(f'{cid}: 端点压在 {b["id"]} 边界上，建议外移 1px')
                    continue
                if seg_rect(x1, y1, x2, y2, b['r']):
                    FAIL.append(f'{cid}: 穿过盒子 {b["id"]}')
                    break

    # 字号与配色收敛度
    sizes = sorted({b['fs'] for b in boxes if b['txt'].strip()})
    if len(sizes) > 4:
        WARN.append(f'字号 {len(sizes)} 种（{sizes}），层级过多，建议收敛到 2–3 种')
    fills = {b['fill'] for b in solid if b['fill'] not in (None, 'none')}
    if len(fills) > 20:
        WARN.append(f'填充色 {len(fills)} 种，配色发散，建议同语义同色')

    seen = set()
    fails = [x for x in FAIL if not (x in seen or seen.add(x))]
    warns = [x for x in WARN if not (x in seen or seen.add(x))]
    print(f'{a.drawio}: 顶点 {len(boxes)} / 连接器 {len(edges)}'
          f'  FAIL {len(fails)}  WARN {len(warns)}')
    for x in fails:
        print(f'  FAIL  {x}')
    for x in warns:
        print(f'  WARN  {x}')
    if fails or (a.strict and warns):
        sys.exit(1)
    print('[OK] 版式体检通过')


if __name__ == '__main__':
    main()
