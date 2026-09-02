# 从零手写 .drawio

模板套不上时走这条路：**直接写 XML**，坐标全部显式给定，然后靠"导出 PNG → 看图 → 改 XML"迭代。
下面的样式串都是在中文示意图上实测可用的，照抄即可。

- [1. 骨架](#1-骨架)
- [2. 先排栅格，再写图元](#2-先排栅格再写图元)
- [3. 样式速查](#3-样式速查)
- [4. 中文排版预算](#4-中文排版预算)
- [5. 连接器](#5-连接器)
- [6. 图标](#6-图标)
- [7. 迭代闭环](#7-迭代闭环)
- [8. 四个必踩的坑](#8-四个必踩的坑)

## 1. 骨架

```xml
<mxfile host="app.diagrams.net" agent="claude-code" version="24.7.17" pages="1">
  <diagram id="fig" name="示意图">
    <mxGraphModel dx="954" dy="1296" grid="0" gridSize="10" guides="1" tooltips="1"
                  connect="1" arrows="1" fold="1" page="1" pageScale="1"
                  pageWidth="954" pageHeight="1296" math="0" shadow="0">
      <root>
        <mxCell id="0" /><mxCell id="1" parent="0" />
        <!-- 图元写在这里 -->
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

顶点与连接器的通用写法：

```xml
<mxCell id="b1" value="盒内文字" style="……" vertex="1" parent="1">
  <mxGeometry x="40" y="60" width="160" height="40" as="geometry" />
</mxCell>

<mxCell id="e1" value="" style="……" edge="1" parent="1">
  <mxGeometry relative="1" as="geometry">
    <mxPoint x="120" y="101" as="sourcePoint" />
    <mxPoint x="120" y="159" as="targetPoint" />
    <Array as="points"><mxPoint x="120" y="130" /></Array>   <!-- 拐点，可省 -->
  </mxGeometry>
</mxCell>
```

**id 用可读的稳定名**（`b2_data`、`e3_agg2math`、`sub_case_bg`），迭代时才能精确定位到某个元素改；
随机 id 会让"改第 37 个盒子"变成大海捞针。

**转义分两种情况**，混淆了要么解析失败要么标签被当字面量显示：

| 内容来源 | 写进 value 时 | 效果 |
|---|---|---|
| 论文/用户/日志里的原文 | 先转义：`a < b` → 写成 `a &lt; b` | 原样显示 `a < b` |
| 你自己加的排版标签 | 同样写成实体：`&lt;br&gt;`、`η&lt;sub&gt;sb&lt;/sub&gt;` | style 带 `html=1`，draw.io 解析成换行/下标 |

两者写法一样，区别只在**意图**：前者是想显示的字面内容，后者是想生效的标签。所以拼接时要先把
原文转义、再拼自己的标签，顺序反了原文里的 `<` 会被当成标签吃掉。

即：`value` 属性里**永远不出现裸 `<`**。写裸 `<br>` 会让 XML 直接解析失败（这一条我踩过）。
用 Python 生成时，源文本一律先 `html.escape(t, quote=True)`，只有自己拼的标签才手动写成 `&lt;br&gt;`。

## 2. 先排栅格，再写图元

不要边想边放。先在纸面/注释里定死三组数：

1. **画布**：竖版示意图常用 954×1296，横版用 1680×1080；
2. **列/行基线**：同族元素共用左边界与宽度，如"左列 x=140 w=144，右列 x=677 w=155"；
3. **步距**：同族纵向步距固定（如 42），族间留 2–3 倍步距。

数量可变的组用等分公式，别手算每个坐标：`size = (span - (n-1)*gap) / n`，第 i 个起点 `a + i*(size+gap)`。

## 3. 样式速查

| 用途 | style |
|---|---|
| 普通盒（圆角） | `rounded=1;arcSize=8;whiteSpace=wrap;html=1;fillColor=#eef6fd;strokeColor=#3b547f;strokeWidth=1;fontSize=16;fontStyle=1;fontColor=#262626;fontFamily=Microsoft YaHei,PingFang SC,Helvetica;align=center;verticalAlign=middle;` |
| 直角盒 | 同上，`rounded=0` |
| 胶囊 | 同上，`rounded=1;arcSize=50` |
| 无边框文字 | `text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;fontSize=16;fontStyle=1;fontColor=#262626;fontFamily=…;` |
| 纯底色块 | `rounded=0;html=1;fillColor=#fdf7ec;strokeColor=none;` |
| 虚线分组框 | `rounded=0;html=1;fillColor=none;strokeColor=#7f5faf;strokeWidth=1;dashed=1;dashPattern=4 4;` |
| 点线分带 | 同上，`dashPattern=1 3` |
| 六边形 | `shape=hexagon;perimeter=hexagonPerimeter2;fixedSize=1;size=12;html=1;fillColor=#bae2e4;strokeColor=#4f8f8b;…` |
| 右向五边形旗标 | `shape=singleArrow;direction=east;arrowWidth=1;arrowSize=0.22;html=1;…;spacingRight=10;`（`arrowWidth=1` 时块箭头退化成五边形） |
| 粗块箭头 | `shape=singleArrow;direction=south;arrowWidth=0.62;arrowSize=0.5;html=1;fillColor=#4874cc;strokeColor=#4874cc;` |
| 灰色双向箭头 | `shape=doubleArrow;html=1;fillColor=#d9d9d9;strokeColor=#9a9a9a;arrowWidth=0.4;arrowSize=0.28;` |
| 圆柱 / 文档 / 平行四边形 | `shape=cylinder3` / `shape=document` / `shape=parallelogram` |

学术克制配色（同族同色，跨族换色）：
蓝 `#eef6fd`/`#3b547f`，橙 `#fcead9`/`#c08b5c`，紫 `#e5dfeb`/`#9b979f`，青 `#dbeef4`/`#668d89`，
灰 `#f2f4f6`/`#8a97a3`；强调块用同族深一档：`#b6d8f6` `#fddecd` `#ccc2db` `#bae2e4`。
连接器 `#1f3f6b`（蓝族）/`#7b5530`（橙族）/`#7f5faf`（紫族）/`#5f8484`（青族）。

描边宽度成体系，不要每个元素随手给：图标轮廓 1–1.5，普通盒与细箭头 1–2，
强调盒 2，粗回路/装饰弯箭头 3–9；容器虚线 1–1.5，`dashPattern` 容器用 `4 4`、分带用 `1 3`。

## 4. 中文排版预算

draw.io 的自动折行对中文很不友好，**一律手动断行**并自己算宽度：

- 全角/中文字符宽 ≈ 字号；半角字母数字空格 ≈ 字号/2；行高 ≈ 字号 + 3。
- 盒子可用宽 = 宽度 − 8。**16px 字号下，一个 160px 宽的盒子每行最多 9 个汉字。**
- 竖排文字要写成逐字堆叠 `破&lt;br&gt;题&lt;br&gt;逻&lt;br&gt;辑`，**不要用 `horizontal=0`**——那是把整块文字旋转 90°，中文会躺倒。竖排每字占 19px。
- 数学符号直接用 Unicode：`η̄ Ē ē × ≤ ÷ ²`，比 `<sub>` 稳；确需下标用 `η&lt;sub&gt;sb&lt;/sub&gt;`。
- 字号建议全图统一（学术模板常是扁平字号），标题最多比正文大一档，不要三四种字号混用。

行级对齐要求高时（比如要给某一行加高亮底条、或多列必须逐行对齐），
**把每一行拆成独立的文字 cell**，高亮矩形垫在该行 cell 后面——靠一个多行盒子里的自动排版对不齐。

`overflow=visible` 只给**没有外框的独立标签**用；有边框的盒子加了它，文字会溢出到框外而不报错。

写完用体检脚本兜住：

```bash
python3 scripts/check_layout.py fig.drawio
```

查文字溢出、越界、id 重复、端点压边、盒子重叠、连线穿盒，中文字宽模型与上面一致。

## 5. 连接器

- **固定坐标**（`sourcePoint`/`targetPoint`）比 `source`/`target` 引用更可控，复刻类图一律用固定坐标；需要拖动后自动跟随时才用引用。
- 折线拐点放进 `<Array as="points">`，配 `edgeStyle=orthogonalEdgeStyle`。
- 平滑曲线：`edgeStyle=none;curved=1` + 2–3 个拐点（正交样式下加 `curved=1` 只会把直角磨圆，不会变成弧）。
- 箭头：实心 `endArrow=block;endFill=1;endSize=5`；空心 `endFill=0;endSize=14`；无箭头 `endArrow=none`（母线段用）。
- 一分多/多合一要画成"竖线 + 横母线 + 分支"，不要画成 N 条独立斜线——语义不同。
- 边上的文字标签：直接写在 edge 的 `value` 上，压线时加 `verticalAlign=bottom` 抬到线上方，或用 `<mxPoint as="offset">` 微调。注意下标会下探压线，`verticalAlign=bottom` 不够时用 `offset` 整体抬 8–10px。

**弯箭头/循环箭头**用曲线连接器，不要用 Unicode 箭头字形，也不要用块箭头形状凑：

```xml
<mxCell id="loop_a" style="edgeStyle=none;curved=1;html=1;endArrow=block;endFill=1;endSize=2;
  strokeWidth=9;strokeColor=#ccccd6;" edge="1" parent="1">
  <mxGeometry relative="1" as="geometry">
    <mxPoint x="330" y="1068" as="sourcePoint" /><mxPoint x="386" y="1050" as="targetPoint" />
    <Array as="points"><mxPoint x="348" y="1040" /></Array>
  </mxGeometry>
</mxCell>
```

两个坑（都实测撞过）：`shape=mxgraph.arrows2.bendArrow` 画出来是**直角 L 形块箭头**，不是弧；
`edgeStyle=orthogonalEdgeStyle` 上加 `curved=1` 只会把直角**磨圆**，仍是折线——必须写
`edgeStyle=none;curved=1`，draw.io 才会按拐点做样条。粗弧配 `endSize=2` 左右，否则箭头巨大。
三段弧首尾相接即可拼出循环。

## 6. 图标

按这个顺序选，**不要一上来就自己画**：

1. 用户提供的图标/logo（最高优先，不要擅自替换）；
2. 自带的 `assets/icons/tabler/outline/`（100 个 MIT 线性图标）与 `icons.md` 里的原语配方，
   别重复造；
3. 用 draw.io 原语拼近似（矩形+椭圆+线+文字符号），**同一类图标复用同一配方、同一描边与尺寸**，
   否则会像一堆互不相干的涂鸦；
4. 实在没有就用带标注的简单符号，并在交付说明里写清这是近似。

内嵌 SVG 的写法（顶点样式，几何要显式给）：

```
shape=image;html=1;imageAspect=1;verticalLabelPosition=bottom;image=data:image/svg+xml;base64,<BASE64>
```

`base64.b64encode(svg_bytes)` 即可。注意：内嵌 SVG **不是** draw.io 原语，无法再拆开编辑，
交付时要说明；Tabler 用 `currentColor`，要改色就先复制一份 SVG 替换颜色再内嵌，别改原文件。

## 7. 迭代闭环

**不看渲染图就不算画完。** XML 里看不出文字溢出、箭头压字、盒子挤扁。

```bash
python3 scripts/check_layout.py fig.drawio          # 先过机器体检
python3 scripts/export_figure.py fig.drawio         # 出 1:1 PNG + 矢量 PDF
```

然后打开 PNG 逐块核对，至少两轮：① 文字是否溢出/压线；② 箭头方向与语义是否一致（尤其分发、汇流、双向）；③ 同族元素是否对齐同宽；④ 数值有没有抄错。看细节可 `-s 2` 出双倍图，或用 Python 裁局部放大。

交付前再确认：XML 能解析；画布尺寸是有意为之；**图里没有 `data:image/png|jpeg` 位图**
（要求可编辑时，位图会让整块无法再改）；标题/图注按需存在或不存在。

## 8. 四个必踩的坑

1. **端点压边**：连接器端点正好落在盒子边界上，会被判成"箭头穿盒"。所有端点离盒边留 1px。
2. **大虚线框 vs 小虚线框**：通用检查器只把「虚线 + 无填充 + >200×100」的顶点当容器豁免。小虚线框请改用闭合折线（四段 edge 首尾相接），否则里面的元素会被判重叠。
3. **底色块**：给分组加底色时用 `strokeColor=none`，它会被当作文本处理，不会与压在上面的盒子判重叠。
4. **外框被遮挡处要断开**：外围回路框穿过标题条/旗标时，把框拆成几段并在被遮挡处留缺口——既符合"线被压在下面"的视觉，也避免误判。

## 与其他参考文件的分工

本文件是**中文示意图的手写速查**。图标与特殊图元看 `icons.md`；静态检查的规则与规避看
`preflight-rules.md`；看图自检的九区盘点、红队与评分卡看 `self-check.md`；**高保真复刻参考图**
（像素标定、四件产物、逐轮比对）走 `replication.md`。XML 写法各处一致，产物可互相接着改。
