# MATLAB MCP Plotting

## Use Criteria

Use this path only when the figure contract requires MATLAB-native results, an installed toolbox,
or a graphics capability that is materially less reliable in Python. Keep ordinary statistical
charts in Python.

## Tool Sequence

1. Call `mcp__matlab__detect_matlab_toolboxes` and verify MATLAB plus the required toolbox.
2. Save a reproducible `.m` file with explicit input and output paths.
3. Call `mcp__matlab__check_matlab_code` and repair errors or relevant warnings.
4. Call `mcp__matlab__run_matlab_file` with the absolute script path.
5. Read command output, verify each exported file exists and is nonempty, then inspect the raster
   preview at target paper width.
6. Reconcile plotted arrays, units, ranges, and annotations with the source artifact.

`mcp__matlab__evaluate_matlab_code` is for short non-destructive probes. Use
`mcp__matlab__run_matlab_test_file` for tested reusable plotting functions.

## Script Contract

```matlab
dataPath = fullfile(projectRoot, "results", "Q1", "tables", "surface.csv");
outDir = fullfile(projectRoot, "paper", "figures");
T = readtable(dataPath);

fig = figure("Color", "w", "Units", "centimeters", ...
    "Position", [2 2 16 11]);
ax = axes(fig);
surf(ax, T.xGrid, T.yGrid, T.objectiveGrid, "EdgeColor", "none");
xlabel(ax, "Parameter x (unit)");
ylabel(ax, "Parameter y (unit)");
zlabel(ax, "Objective value (unit)");
set(ax, "FontName", "Arial", "FontSize", 8, "Box", "off");
colorbar(ax);
view(ax, 35, 28);

exportgraphics(fig, fullfile(outDir, "fig_q1_surface.pdf"), ...
    "ContentType", "vector");
exportgraphics(fig, fullfile(outDir, "fig_q1_surface.png"), ...
    "Resolution", 300);
close(fig);
```

Adapt the code to the verified data shape; do not paste this example without checking table fields
and array dimensions.

## Failure Handling

- MATLAB missing: return to Python or report a backend blocker.
- Toolbox missing: choose a toolbox-free implementation or return to Python.
- Code Analyzer issue: repair before execution unless the warning is documented and irrelevant.
- Execution error: inspect the exact MATLAB message; never infer output.
- Export missing or blank: fail the figure, repair, and rerun.
- Visual QA failure: edit the `.m` script and repeat check/run/inspection.
