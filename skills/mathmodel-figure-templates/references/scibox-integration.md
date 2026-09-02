# sci-box figure integration

The local `scibox-figure` skill is installed separately for discovery and upstream comparison.
MathModeling Skills intentionally keeps one canonical copy under `mathmodel-figure-templates`:
the template scripts are already integrated, while this plugin adds contest-specific constraints
for source-bound data, non-decorative panels, readable labels, and effective raster resolution.

When a request matches a sci-box template, use the canonical renderer and replace all simulated
values with verified project data before promotion to a paper figure. Keep SVG text editable where
possible, record the source data path and insertion dimensions, and enforce the plugin's hard
minimum of 7.5 pt (Chinese sixth-size) after final scaling. A 300 dpi export is useful but is not
an absolute pass/fail threshold; the image must remain sharp at the actual paper size.

Do not copy a second full `scibox-figure` skill into the plugin. If upstream later adds a genuinely
new template, port only that template and its required references after checking license and
compatibility with `modeling-figure-orchestrator`.
