# MathModeling Skills Sources

This unified local Codex plugin contains skills from multiple sources:

- `C:\MathModeling-skills\.codex\skills` (30 skills, including standardized Draw.io MCP execution and modeling-abstract writing)
- `jihe520/MathModelAgent` (10 skills previously installed into Codex; `_references` was normalized to `mathmodel-references` for valid plugin naming)
- `RealSeaberry/AutoMCM-Pro` (4 skills plus the required runtime scripts, templates, SOP, README, and MIT license)
- `jihe520/sci-box` (scientific-figure templates plus the `scibox-diagram` Draw.io layouts,
  generators, preview/export tooling, and layout checker; integrated diagram resources reside
  under `skills/4drawio/resources/scibox-diagram/`). The bundled Tabler Icons retain their MIT
  attribution and license in that resource directory.
- Local `academic-research-skills` plugin v3.18.0 by Cheng-I Wu, sourced from `https://github.com/Imbad0202/academic-research-skills` (adapted snapshots of `deep-research`, `academic-paper`, and `academic-paper-reviewer`; upstream framework preserved under CC-BY-NC-4.0, with math-modeling-specific routing and gate overrides)
- `https://github.com/ChenLiu-1996/figures4papers`, reviewed at commit `565e6b97a9609e14ac07bee83dcb94589034fe27`, is referenced by `math-figure-generator` for optional publication-figure precedents. No upstream code or assets are bundled because the reviewed repository has no license file.

`academic-pipeline` was intentionally not copied because `workflow-orchestrator` remains the sole
top-level scheduler for this plugin.

The plugin contains copied snapshots so Codex can load the complete collection under the
`mathmodeling-skills` namespace. Canonical source directories are maintained separately and may
contain newer local edits that are mirrored into this installed snapshot deliberately.
