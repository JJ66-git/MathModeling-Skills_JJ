#!/usr/bin/env python3
"""export_figure.py — 把 .drawio 导成 1:1 PNG 与矢量 PDF，供肉眼自检和交付。

    python3 export_figure.py fig.drawio                 # 出 fig.png + fig.pdf
    python3 export_figure.py fig.drawio --png-only -s 2 # 只出 2 倍图，便于看细节

依赖 draw.io 桌面版命令行（macOS: brew install --cask drawio；命令名 drawio）。
没装时会给出替代方案，不静默失败。
"""
import argparse
import pathlib
import re
import shutil
import subprocess
import sys


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if p.returncode != 0:
        print(p.stdout + p.stderr, file=sys.stderr)
    return p.returncode == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('drawio')
    ap.add_argument('-s', '--scale', type=float, default=1, help='PNG 缩放，默认 1（1 单位=1 像素）')
    ap.add_argument('--png-only', action='store_true')
    ap.add_argument('--pdf-only', action='store_true')
    a = ap.parse_args()

    src = pathlib.Path(a.drawio)
    if not src.exists():
        sys.exit(f'找不到 {src}')
    cli = shutil.which('drawio')
    if not cli:
        sys.exit('未找到 drawio 命令行。\n'
                 '  macOS: brew install --cask drawio\n'
                 '  或：用 diagrams.net 网页版打开 .drawio 后 File → Export as → PNG/PDF\n'
                 '  注意：没有渲染图就无法自检，不要跳过这一步。')

    # 用画布宽度锁定输出，保证 1 单位 = 1 像素；否则 drawio 会按内容包围盒另算，
    # 输出比画布大几像素，没法和参考图做逐像素比对
    m = re.search(r'pageWidth="([\d.]+)"', src.read_text(encoding='utf-8'))
    width = [f'--width', str(int(float(m.group(1)) * a.scale))] if m else []

    ok = True
    if not a.pdf_only:
        png = src.with_suffix('.png')
        ok &= run([cli, '-x', '-f', 'png', '-s', str(a.scale), '-b', '0',
                   *width, '-o', str(png), str(src)])
        if ok:
            print(f'[OK] {png}')
    if not a.png_only:
        pdf = src.with_suffix('.pdf')
        ok &= run([cli, '-x', '-f', 'pdf', '--crop', '-o', str(pdf), str(src)])
        if ok:
            print(f'[OK] {pdf}')
    if not ok:
        sys.exit(1)
    print('接下来务必打开 PNG 逐块核对：文字有无溢出/压线、箭头方向、数值有没有抄错。')


if __name__ == '__main__':
    main()
