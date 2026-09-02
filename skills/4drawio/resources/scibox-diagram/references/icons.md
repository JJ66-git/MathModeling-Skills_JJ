# 图标与特殊图元

## 选择顺序

1. **用户提供的图标 / logo** —— 最高优先，不要擅自替换成"看起来差不多"的。
2. **`assets/icons/tabler/outline/` 里的 SVG** —— 100 个线性图标，MIT 许可，风格统一，直接内嵌。
3. **用 draw.io 原语拼** —— 下面有配方；同一类图标务必复用同一配方、同一描边宽度和尺寸，否则会像一堆互不相干的涂鸦。
4. **退化为带文字标签的简单符号** —— 并在交付说明里写清这是近似。

复杂写实图标（设备外形、地图、人物）不要硬拼，宁可用 Tabler 里语义接近的，或直接向用户要素材。

## 内嵌 Tabler 图标

现成图标覆盖：数据与存储（`database` `server` `folder` `archive` `box`）、计算（`cpu` `robot` `brain` `atom` `binary`）、流程与结构（`sitemap` `hierarchy` `schema` `git-branch` `git-merge` `route` `timeline` `stack` `layers-intersect`）、图表（`chart-line` `chart-bar` `chart-dots` `graph` `math-function` `sum`）、动作（`filter` `search` `refresh` `repeat` `transfer` `arrows-split` `arrows-join`）、状态（`circle-check` `circle-x` `alert-triangle` `shield-check` `target` `trophy`）、器材（`microscope` `flask` `camera` `video` `microphone`）等。先 `ls assets/icons/tabler/outline/` 看有没有再动手画。

```python
import base64, pathlib
svg = pathlib.Path('assets/icons/tabler/outline/database.svg').read_bytes()
uri = 'data:image/svg+xml;base64,' + base64.b64encode(svg).decode()
style = f'shape=image;html=1;imageAspect=1;verticalLabelPosition=bottom;verticalAlign=top;image={uri};'
```

配上显式几何（图标建议 24–32 px 见方，同图内统一）：

```xml
<mxCell id="ic_db" value="数据库" style="shape=image;html=1;imageAspect=1;image=data:image/svg+xml;base64,…"
        vertex="1" parent="1">
  <mxGeometry x="120" y="200" width="28" height="28" as="geometry" />
</mxCell>
```

两点注意：内嵌 SVG **不是** draw.io 原语，无法再拆开逐段编辑，交付时要说明；Tabler 用
`currentColor` 描边，要换色就先复制一份 SVG 改掉颜色再内嵌，别动 `assets/` 里的原文件。

## 原语配方

以下都是实际画过、渲染验证过的写法，直接抄样式串。

**右向五边形旗标**（阶段标签）——块箭头把箭杆撑满高度就退化成五边形：

```
shape=singleArrow;direction=east;arrowWidth=1;arrowSize=0.22;html=1;fillColor=#98d0ed;strokeColor=#5b93bd;spacingRight=10;
```

**粗块箭头**（阶段推进）：

```
shape=singleArrow;direction=south;arrowWidth=0.62;arrowSize=0.5;html=1;fillColor=#4874cc;strokeColor=#4874cc;
```

**双向箭头**（互相印证、对照关系）：

```
shape=doubleArrow;html=1;fillColor=#d9d9d9;strokeColor=#9a9a9a;arrowWidth=0.4;arrowSize=0.28;
```

**空心宽箭头**（两侧对向汇入）——用带空心箭头的短边，比塞一个形状更省地方：

```
edgeStyle=orthogonalEdgeStyle;html=1;endArrow=block;endFill=0;endSize=14;strokeWidth=2;strokeColor=#3b547f;
```

**手绘风弯箭头 / 循环**——粗描边曲线连接器，三段首尾相接即成环：

```
edgeStyle=none;curved=1;html=1;endArrow=block;endFill=1;endSize=2;strokeWidth=9;strokeColor=#ccccd6;
```

坑：`shape=mxgraph.arrows2.bendArrow` 出来是**直角 L 形块箭头**不是弧；在
`edgeStyle=orthogonalEdgeStyle` 上加 `curved=1` 只会把直角**磨圆**，仍是折线。必须
`edgeStyle=none;curved=1` 才走样条。粗弧配 `endSize=2` 左右，否则箭头巨大。

**六边形 / 胶囊 / 圆柱 / 文档 / 平行四边形**：

```
shape=hexagon;perimeter=hexagonPerimeter2;fixedSize=1;size=12;html=1;
rounded=1;arcSize=50;html=1;                     ← 胶囊
shape=cylinder3;html=1;boundedLbl=1;backgroundOutline=1;   ← 数据库
shape=document;html=1;    shape=parallelogram;html=1;
```

**描边宽度成体系**：图标轮廓 1–1.5，普通盒与细箭头 1–2，强调盒 2，粗回路 3–9。同一张图里别混。

## 记账

用了近似或内嵌位图/SVG 的地方，在交付说明（复刻任务则在 `asset-ledger.md`）里写清：原图是什么、
用什么近似的、差在哪。**不要悄悄省略元素**——漏画比画得糙严重得多。
