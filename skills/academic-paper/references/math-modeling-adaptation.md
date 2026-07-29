# Math Modeling Adaptation

## Authority Order

Apply these sources in order:

1. Contest rules, official template, page limit, language, and submission requirements.
2. `workflow-orchestrator` gates and human decision artifacts.
3. `frozen_numbers.json`, decision logs, final method explanations, and robustness reports.
4. `qx_solution_package_for_writer.md` for each subquestion.
5. This adaptation and the original academic-paper framework.

The original 12-agent framework supplies architecture, argumentation, drafting discipline,
revision, citation checking, and prose quality. It does not reopen modeling decisions or experiments.

## Entry Gates

Architecture-only work may begin after Gate G1, but it must contain no unsupported numerical claims.
Detailed drafting requires, for every included Qx:

- `methods/Qx/qx_final_method_explanation.md`;
- `results/Qx/reports/qx_final_result_analysis.md`;
- `results/Qx/reports/qx_solution_package_for_writer.md`;
- `results/Qx/reports/frozen_numbers.json`;
- applicable robustness report and figure plan.

If any required artifact is missing, stop that Qx and return to `workflow-orchestrator`. Never infer
the missing content from raw outputs.

## Contest Paper Structure

Use the official template. When no template fixes the order, prefer:

1. Summary or abstract with key methods, verified results, and conclusions.
2. Problem restatement and analysis.
3. Assumptions and notation.
4. Data preparation.
5. Per-subquestion model formulation, solution, results, and interpretation.
6. Sensitivity, robustness, and error analysis.
7. Model strengths, weaknesses, and limitations.
8. References and appendices.

Do not default to journal IMRaD, APA 7, bilingual abstracts, CRediT, funding, data availability,
ethics, conflict-of-interest, or AI-disclosure sections. Include any of them only when the contest
rules or user explicitly require them.

## Claim-Evidence Contract

Every substantive sentence maps to one evidence class:

| Claim | Canonical source |
|---|---|
| Numerical value | `frozen_numbers.json` entry |
| Why a method was selected | Human `decision_id` |
| Formula or algorithm | Final method explanation |
| Empirical result | Final result analysis and run summary |
| Stability or limitation | Robustness report |
| External factual claim | Verified reference |

The writer may improve organization and language but must preserve equations, symbols, units,
signs, precision, ranking, and claim strength. New numerical analysis requires returning to the
modeling/code workflow and re-freezing results.

## Original Agent Mapping

- `intake_agent`: read contest configuration and existing modeling artifacts; do not start a second
  paper pipeline.
- `literature_strategist_agent`: consume `planning/literature/` and `reference-manager` outputs.
- `structure_architect_agent`: create the global contest-paper outline and page budget.
- `argument_builder_agent`: construct claim-evidence chains from solution packages and decision IDs.
- `draft_writer_agent`: delegate per-Qx prose to `paper-section-writer`; never write around its gates.
- `citation_compliance_agent`: coordinate with `reference-manager`.
- `abstract_bilingual_agent`: write the required summary language only; bilingual output is optional.
- `peer_reviewer_agent`: provide an internal writing check, not the independent G6 audit.
- `formatter_agent`: coordinate with `5writing` and `typst-author`.
- `visualization_agent`: coordinate with `figure-table-planner` and data-driven figure skills.
- `revision_coach_agent`: convert feedback into a scoped revision map without changing canonical
  model facts.
- `socratic_mentor_agent`: help the human frame contribution and narrative without authoring graded
  modeling judgments.

## Supported Modes

- `plan` / `outline-only`: global structure, page budget, and evidence map.
- `full`: writing enhancement over canonical artifacts; still use `paper-section-writer` per Qx.
- `abstract-only`: write the contest summary after the body and frozen results are stable.
- `citation-check`: run with `reference-manager` and verify every source.
- `format-convert`: route layout work to `5writing` / `typst-author`.
- `revision` / `revision-coach`: produce a scoped revision plan and patch only affected prose.

Do not use `lit-review` when `deep-research` plus `related-paper-analyzer` already produced the
literature handoff. Disclosure and rebuttal modes run only when the contest explicitly requires
those artifacts.

## Outputs

```text
paper/planning/global_outline.md
paper/planning/page_budget.md
paper/planning/claim_evidence_map.md
paper/planning/argument_blueprint.md
paper/reviews/writing_quality_check.md
paper/revisions/revision_roadmap.md
```

Final source files remain under the existing `paper/` structure selected by `5writing`.

## Runtime Boundary

This bundled derivative does not include upstream `shared/`, `.claude/`, `docs/`, or root `scripts/`
runtime files. Do not invoke `academic-pipeline`, Material Passport, sprint-contract, phase-boundary
hooks, or deterministic patch scripts that are absent. Do not claim those checks ran. Use the
`mathmodeling-skills` gates and bundled resources instead.
