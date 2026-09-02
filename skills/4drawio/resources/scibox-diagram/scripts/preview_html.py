#!/usr/bin/env python3
"""preview_html.py — 在浏览器里预览 .drawio（不依赖 draw.io 桌面版）。

    python3 preview_html.py fig.drawio             # 生成预览页并起本地服务
    python3 preview_html.py fig.drawio --no-serve  # 只生成 HTML
    python3 preview_html.py fig.drawio --port 8790

优先用 `export_figure.py` 出 1:1 PNG 自检；本脚本用于没装 drawio 命令行、或想在浏览器里
直接改图的场景。XML 内联进页面再 postMessage 给 embed.diagrams.net，避免把整张图塞进 URL
（长 URL 在 Windows 上会直接失败）。

注意：页面里的"保存"是**下载**一份 .drawio，不会写回原文件；改完要手动拷回工作目录。
"""
import argparse
import html
import http.server
import json
import pathlib
import socketserver
import threading
import webbrowser

PAGE = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>%(title)s</title>
<style>html,body{margin:0;height:100%%;font-family:system-ui,sans-serif}
#bar{height:34px;line-height:34px;padding:0 12px;background:#f2eef7;border-bottom:1px solid #ddd;font-size:13px}
iframe{width:100%%;height:calc(100%% - 35px);border:0}</style></head>
<body><div id="bar">%(title)s —— 页面内保存为下载，不会写回原文件</div>
<iframe id="fr" src="https://embed.diagrams.net/?embed=1&proto=json&spin=1&ui=atlas&libraries=0&grid=0"></iframe>
<script>
const XML = %(xml)s;
window.addEventListener('message', function (e) {
  if (e.origin !== 'https://embed.diagrams.net') return;
  let m; try { m = JSON.parse(e.data); } catch (_) { return; }
  if (m.event === 'init') {
    document.getElementById('fr').contentWindow.postMessage(
      JSON.stringify({ action: 'load', autosave: 0, xml: XML }), '*');
  }
});
</script></body></html>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('drawio')
    ap.add_argument('--port', type=int, default=8790)
    ap.add_argument('--no-serve', action='store_true')
    a = ap.parse_args()

    src = pathlib.Path(a.drawio)
    if not src.exists():
        raise SystemExit(f'找不到 {src}')
    out = src.with_suffix('.preview.html')
    out.write_text(PAGE % {'title': html.escape(src.name),
                           'xml': json.dumps(src.read_text(encoding='utf-8'))},
                   encoding='utf-8')
    print(f'[OK] {out}')
    if a.no_serve:
        return

    root = out.parent.resolve()

    class H(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *ar, **kw):
            super().__init__(*ar, directory=str(root), **kw)

        def log_message(self, *_):
            pass

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(('127.0.0.1', a.port), H) as srv:
        url = f'http://127.0.0.1:{a.port}/{out.name}'
        print(f'预览: {url}   （Ctrl-C 结束）')
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            print('\n已停止')


if __name__ == '__main__':
    main()
