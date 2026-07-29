# Math Modeling Adaptation

## Role

Use the original independent panel structure to simulate mathematical modeling competition judges.
This is a read-only advisory review after a complete draft exists and before the three Gate G6
audits. It may recommend revisions but cannot edit the manuscript or certify final submission.

## Required Inputs

- Official problem statement, rules, template, and page limit.
- Complete paper source and compiled PDF when available.
- `planning/symbol_table.md` and model assumptions.
- Per-Qx final method explanations, decision logs, solution packages, frozen numbers, run summaries,
  robustness reports, code reviews, and figure plan.

If the paper cannot be traced to these artifacts, mark the affected claims `UNVERIFIABLE`; do not
fill gaps from reviewer intuition.

## Five Contest Reviewer Personas

| Original seat | Mathematical modeling responsibility |
|---|---|
| EIC | Head judge: problem coverage, contest compliance, page economy, overall coherence |
| Methodology reviewer | Equations, assumptions, objectives, constraints, solver validity, baselines, reproducibility |
| Domain reviewer | Correct interpretation of domain mechanisms, units, data semantics, and practical plausibility |
| Perspective reviewer | Result communication, figures, sensitivity, usability, transferability, and reader experience |
| Devil's Advocate | Counterexamples, alternative models, fragile assumptions, leakage, overclaiming, and failure boundaries |

The panel must remain perspective-diverse. Duplicate criticisms are merged with distinct evidence,
not repeated to simulate consensus.

## Review Contract

Each finding contains:

- severity: `BLOCKING`, `MAJOR`, or `MINOR`;
- exact paper location;
- violated contest or modeling criterion;
- canonical artifact used for verification;
- observed evidence;
- concrete repair owner and next skill.

Review every Qx separately before judging the whole paper. Verify numerical claims against
`frozen_numbers.json`, method-selection prose against human decision IDs, formulas against final
method explanations, and limitations against robustness reports.

Use contest decisions instead of journal decisions:

- `READY_FOR_G6`: no blocking issue; proceed to independent audits.
- `REVISE_BEFORE_G6`: major issues remain but are repairable.
- `BLOCKED_UPSTREAM`: a model, result, freeze, or human-decision artifact is invalid or missing.

A Devil's Advocate `BLOCKING` finding forbids `READY_FOR_G6`.

## Outputs

```text
paper/reviews/modeling-panel/
  reviewer_configuration.md
  head_judge_review.md
  methodology_review.md
  domain_review.md
  perspective_review.md
  devils_advocate_review.md
  panel_decision.md
  revision_roadmap.md
```

In `re-review` mode, add `revision_traceability_matrix.md` and verify each claimed repair against the
revised paper and canonical artifacts.

## Gate G6 Boundary

This panel adds breadth but does not replace:

- `consistency-auditor` for cross-media factual consistency;
- `completeness-auditor` for required artifacts and human-decision records;
- `quality-assurance-auditor` for final workflow and submission quality.

Only those three audits can pass Gate G6. A panel result is an optional input to them.

## Runtime Boundary

This bundled derivative does not include upstream `shared/`, `.claude/`, `docs/`, or root `scripts/`
runtime files. Do not invoke `academic-pipeline`, cross-model upload, calibration runs, sprint
contracts, Material Passport, or phase-boundary hooks unless their complete runtime and explicit
user authorization are available. Do not claim unavailable checks ran.
