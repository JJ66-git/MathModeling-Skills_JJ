# Visual QA Contract

## Automated Checks

| Check | Pass condition |
|---|---|
| Source | Exact path exists; plotted fields and transforms are recorded |
| Values | Counts, ranges, extrema, ordering, units, and key labels match source |
| Font | Final scaled size >=7.5 pt (Chinese sixth-size/六号); no annotation exemption below the floor |
| Canvas | No text, legend, annotation, axes, or panel is clipped |
| Overlap | No unintended text/text, text/data, legend/data, or panel collision |
| Axes | Labels, units, ticks, scales, and reference lines are explicit |
| Color | Semantic, consistent, color-vision-safe, and legible in grayscale |
| Dimensions | Single-column figure fills the text width; spanning figure stays within the text block; paper-figure height >=5 cm |
| Density | Same-theme evidence is merged; each panel adds distinct information; dual axes have explicit units, scales, and justification |
| Annotation | Key values, meaningful extrema, uncertainty/error bars or confidence intervals, and baseline are `present` or `N/A: reason` |
| Export | Prefer vector; for raster record pixels, insertion size, and effective resolution (有效分辨率); no universal 300 dpi gate |
| Provenance | Figure contract, generator, source, backend, and claim status recorded |

For a raster inserted at width `W_in` inches, compute `effective_dpi = pixel_width / W_in` (and
check height equivalently). Official contest or template rules take precedence. Without a stated
rule, use 240 effective dpi as the normal bitmap insertion target and repair any output that looks
soft, jagged, or unreadable at target width. A vector paper figure still needs a rasterized preview
for visual inspection, but the preview's DPI is not a substitute for checking the vector itself.

Use `math-figure-generator`'s render-check for matplotlib figures. For MATLAB and DrawIO outputs,
perform equivalent file, geometry, text, and target-width checks and log them explicitly.

## Target-Width Visual Inspection

1. Open the exported PNG or a rasterized PDF/SVG preview, not the interactive canvas.
2. Scale it to the width used by the contest template.
3. Inspect the full page view for hierarchy and the 100% crop for text and line quality.
4. Check the longest label, densest legend, smallest panel, and closest annotation pair.
5. Check whether a reader can identify the claim, variables, units, and method mapping without
   guessing.
6. Measure the smallest rendered text after paper scaling; anything below 7.5 pt is a failure.
7. Check the final width, >=5 cm height, raster effective resolution, and print-scale sharpness.
8. Repair the generator and re-export; do not patch pixels in the final image.

## Human-Crafted Style Review

Pass when the figure is tailored to its evidence: deliberate ordering, meaningful direct labels,
restrained annotation, balanced whitespace, purposeful panel ratios, and a consistent semantic
palette. Fail generic defaults, decorative noise, gratuitous 3D, rainbow colors, misleading axis
compression, or style differences that imply false semantic differences.

## Promotion Decision

- `PASS`: correctness, claim, automated checks, and target-width inspection all pass.
- `REPAIR`: rendering or styling defect with correct upstream data.
- `BLOCKED_UPSTREAM`: source, result, claim, or flow logic is missing or inconsistent.

Only `PASS` Type 3/4 figures may enter the final paper.
