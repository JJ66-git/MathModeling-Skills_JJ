# Figures4Papers Reference

## Source status

- Repository: [ChenLiu-1996/figures4papers](https://github.com/ChenLiu-1996/figures4papers)
- Reviewed commit: `565e6b97a9609e14ac07bee83dcb94589034fe27`
- Role: optional visual and implementation reference for publication-targeted Matplotlib figures
- Dependency status: external reference only; figure generation must still work when the repository is unavailable

The reviewed repository contains project-specific Python scripts and rendered examples plus a
`scientific-figure-making` guide. It does not currently include a license file. Do not vendor,
redistribute, or copy its scripts, images, palettes, or skill files into this plugin or a contest
submission. Independently implement the selected presentation pattern with the project's verified
data and this plugin's local conventions.

## When to consult it

Consult the repository after the figure contract is frozen and before implementing a
publication-targeted Matplotlib figure when a concrete visual precedent would improve:

| Need | Closest upstream examples |
|---|---|
| Grouped comparison or ablation bars | `figure_ImmunoStruct`, `figure_CellSpliceNet`, `figure_Brainteaser` |
| Trend or multi-line comparison | `figure_VIGIL`, `figure_ophthal_review` |
| Heatmap or parameter sweep | `figure_RNAGenScape`, `figure_ophthal_review` |
| Radar or polar comparison | `figure_VIGIL` |
| Multi-panel comparison or trajectory layout | `figure_Cflows`, `figure_RNAGenScape` |
| Geometric concept rendered with Matplotlib | `figure_Dispersion` |

Choose the closest example by evidence structure, not by visual novelty. Inspect only the relevant
project folder and, when needed, the upstream `scientific-figure-making` reference. Do not preload
or imitate every demo.

## Priority and adaptation rules

Apply this order of authority:

1. verified project data, units, transformations, and frozen results;
2. the human-confirmed `core_claim`, panel map, paper placement, and target dimensions;
3. this plugin's source traceability, semantic color consistency, paper-language labels, editable
   SVG/PDF text, scaled font-size, render-check, visual inspection, manifest, and G5/G6 gates;
4. Figures4Papers layout, typography, legend, spine, annotation, and export ideas.

Borrow a pattern only when it makes the confirmed claim easier to read. Recalculate dimensions,
font sizes, axis ranges, annotations, legend placement, and palette for the contest paper at its
actual insertion width. Never copy upstream numbers, labels, scientific claims, or project-specific
semantics. Tight axis limits must remain honest and clearly labeled; they must not exaggerate a
difference or hide a relevant baseline.

Record the selected upstream folder or file URL in the internal figure manifest as
`visual_reference`; do not cite it as evidence for model results. Academic citations remain tied to
the actual methods, data, and claims used by the paper.

## Boundaries

Do not use this reference as the primary route for:

- Draw.io workflow, architecture, or exact logical diagrams;
- interactive Plotly/Bokeh/Altair dashboards;
- GIS or map-first figures;
- dominant 3D rendering or non-Matplotlib illustration workflows;
- exploratory-only plots with no publication target;
- copying upstream image assets into a paper.

Route those cases through `modeling-figure-orchestrator`. If GitHub is unreachable or the reviewed
paths have changed, continue with the local `math-figure-generator` patterns and record
`visual_reference: unavailable`; external availability must not block a required figure.
