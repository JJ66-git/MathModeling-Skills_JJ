# MathModeling Skills Sources

This unified local Codex plugin contains skills from multiple sources:

- `C:\MathModeling-skills\.codex\skills` (28 skills)
- `jihe520/MathModelAgent` (10 skills previously installed into Codex; `_references` was normalized to `mathmodel-references` for valid plugin naming)
- `RealSeaberry/AutoMCM-Pro` (4 skills plus the required runtime scripts, templates, SOP, README, and MIT license)
- Local `academic-research-skills` plugin v3.18.0 by Cheng-I Wu, sourced from `https://github.com/Imbad0202/academic-research-skills` (adapted snapshots of `deep-research`, `academic-paper`, and `academic-paper-reviewer`; upstream framework preserved under CC-BY-NC-4.0, with math-modeling-specific routing and gate overrides)

`academic-pipeline` was intentionally not copied because `workflow-orchestrator` remains the sole
top-level scheduler for this plugin.

The source directories remain unchanged. The plugin contains copied snapshots so Codex can load
the complete collection under the `mathmodeling-skills` namespace.
