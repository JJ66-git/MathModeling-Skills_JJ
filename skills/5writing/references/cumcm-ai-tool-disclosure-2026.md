# CUMCM AI Tool Disclosure (2026 Trial)

Use this reference only for the National College Student Mathematical Modeling Contest (CUMCM) when the 2026 trial rules apply. The rules take effect on September 1, 2026.

## Non-negotiable principle

The disclosure is a factual compliance record, not a preferred narrative. Never conceal, narrow, or fabricate AI use. A desired claim such as "AI was used only for code debugging" is valid only when the complete contest record supports it. Deliberately concealing AI use or making a false declaration may result in disqualification from awards.

## Required paper statement

Insert an unnumbered section titled `AI 工具使用声明` immediately before the references.

Choose exactly one evidence-supported branch:

### No AI used anywhere in the contest

```text
本参赛队在竞赛过程中未使用任何 AI 工具。
```

Do not create a fictitious usage-detail report for this branch.

### AI used during the contest

```text
本参赛队在竞赛过程中使用了 AI 工具，主要用于【简要用途，如语言润色、代码调试等】，详细使用情况见支撑材料。
```

When the evidence proves that code debugging was the only AI-assisted activity, replace the bracketed text with `代码调试`:

```text
本参赛队在竞赛过程中使用了 AI 工具，主要用于代码调试，详细使用情况见支撑材料。
```

When the evidence shows that AI was used for code debugging and to provide non-final scaffolds that the team subsequently rebuilt and verified, use:

```text
本参赛队在竞赛过程中使用了 AI 工具，主要用于代码调试及前期框架辅助，详细使用情况见支撑材料。
```

If any other substantive use occurred, list the actual uses concisely instead. Do not use either narrow sentence to hide a broader use.

## Placement examples

Typst:

```typst
#heading(level: 1, outlined: false)[AI 工具使用声明]

本参赛队在竞赛过程中使用了 AI 工具，主要用于代码调试，详细使用情况见支撑材料。

// The references block follows immediately.
```

LaTeX:

```latex
\section*{AI 工具使用声明}
本参赛队在竞赛过程中使用了 AI 工具，主要用于代码调试，详细使用情况见支撑材料。

% The bibliography follows immediately.
```

Use the no-AI sentence instead when that branch is supported. Preserve the official Chinese wording and keep this section before the bibliography in the compiled PDF.

For the framework-assistance branch, replace the body sentence in the same Typst or LaTeX structure with:

```text
本参赛队在竞赛过程中使用了 AI 工具，主要用于代码调试及前期框架辅助，详细使用情况见支撑材料。
```

## Evidence gate

Before choosing a branch, inspect all records available to the team:

- AI chat/export history and tool activity logs;
- source-control history and diffs;
- IDE, notebook, terminal, build, and test logs;
- modeling notes, figure-generation records, reference-search records, and paper revision history;
- team members' signed or otherwise attributable usage records.

Build an internal phase matrix with one row for each of these phases:

| Phase | AI status | Evidence | Allowed final wording |
|---|---|---|---|
| Problem understanding and restatement | Used / Not used / Unknown | Record location or team confirmation | `未使用` only when verified |
| Model selection and mathematical derivation | Used / Not used / Unknown | Record location or team confirmation | `未使用` only when verified |
| Data cleaning and analysis | Used / Not used / Unknown | Record location or team confirmation | `未使用` only when verified |
| Algorithm and code creation | Used / Not used / Unknown | Record location or team confirmation | Do not merge code creation into debugging |
| Code debugging | Used / Not used / Unknown | Interaction and test records | `使用` when verified |
| Figure and table production | Used / Not used / Unknown | Figure provenance | `未使用` only when verified |
| Literature retrieval and citation | Used / Not used / Unknown | Search and reference records | `未使用` only when verified |
| Paper drafting, translation, and polishing | Used / Not used / Unknown | Revision history | `未使用` only when verified |

Any `Unknown` affecting the declaration blocks finalization. Ask the team to resolve it from records; do not infer `Not used` from silence.

## What counts as code debugging

Code-debugging use may include:

- interpreting an actual syntax, runtime, dependency, convergence, or numerical-stability error;
- locating a defect in an existing team-written implementation;
- suggesting a minimal patch, diagnostic assertion, or regression test;
- explaining a stack trace or environment mismatch.

The following are not code debugging and must be disclosed separately when AI-assisted:

- selecting the model, objective function, constraints, algorithm, or evaluation method;
- deriving formulas or deciding parameters from the contest problem;
- generating the substantive solution implementation from scratch;
- performing data analysis or interpreting contest results;
- generating figures, tables, literature, citations, or paper prose;
- translating or polishing the paper.

## What counts as early framework assistance

`前期框架辅助` is a concise disclosure category, not an exemption from reporting the affected stages. In the detail PDF, name every actual scaffold produced, such as:

- a candidate modeling workflow or checklist that the team independently evaluated;
- a code-module skeleton or pseudocode structure later rewritten by the team;
- a paper outline or provisional paragraph structure later substantively rewritten;
- a data-processing pipeline outline, figure plan, or diagram layout later implemented and checked by the team.

Do not label final formulas, final implementation, computed results, final figures, citations, or substantially retained prose merely as a scaffold. If such output was used, disclose the specific use and adoption status.

Extensive human revision does not retroactively mean that AI was unused. It changes the adoption record: state whether the output was structurally referenced, partially adopted, fully replaced, or rejected, then identify the human reconstruction and its verification evidence.

## Required supporting PDF

For every AI-used branch, create:

```text
supporting-materials/AI 工具使用详情.pdf
```

Keep an editable source beside it, using the selected paper engine, for example `AI 工具使用详情.typ` or `AI 工具使用详情.tex`. Do not finalize the PDF while any bracketed field remains, any tool/version is guessed, or a claimed verification cannot be reproduced.

The PDF must contain all four required categories:

1. AI tool name and version or model.
2. Specific purpose and workflow stage.
3. Main prompting method and usage process; genuine typical interactions may be attached.
4. Adoption, human modification, and verification of AI output. The regulation's language-polishing exception does not remove this requirement for code-debugging use.

## Code-debugging-only report template

Use the following content only after the phase matrix proves that all non-debugging phases were AI-free. Replace every bracketed field with verified facts.

```markdown
# AI 工具使用详情

## 一、AI 工具基本信息

| 序号 | AI 工具名称 | 版本或模型 | 使用账号/访问方式 | 使用日期与时间范围 |
|---|---|---|---|---|
| 1 | [按日志填写工具名称] | [按界面或日志填写版本/模型] | [网页端/客户端/API/IDE 插件] | [YYYY-MM-DD HH:MM--HH:MM] |

## 二、具体使用目的和环节

本参赛队仅在代码调试环节使用上述 AI 工具。具体用途限于分析已有程序运行时出现的[语法错误/运行时错误/依赖冲突/数值稳定性问题/收敛异常]，协助定位可能原因，并提出最小修改建议或验证思路。模型选择、数学推导、算法方案确定、数据处理与结果分析、图表制作、文献检索与引用、论文撰写、翻译和语言润色等环节均未使用 AI 工具。

上述范围已经由参赛队结合 AI 交互记录、代码版本差异、终端运行记录和团队成员记录逐项核对。

## 三、主要提示方式与使用过程

使用时，参赛队仅向 AI 提供复现错误所需的最小信息，包括报错信息、相关代码片段、运行环境和预期行为，不要求 AI 选择模型、推导公式、生成完整算法或解释竞赛结果。基本过程如下：

1. 由队员独立复现错误并保存报错信息和对应代码版本。
2. 向 AI 提交错误现象、最小代码片段、环境信息及已完成的排查步骤。
3. 将 AI 返回的候选原因和修改建议与程序逻辑逐项比对。
4. 由队员人工修改代码，并运行原始算例、边界算例和回归测试。
5. 记录采纳状态、人工修改内容、验证命令和验证结果。

### 典型交互记录 [编号]

- 时间：[YYYY-MM-DD HH:MM]
- 对应文件与代码版本：[相对路径及提交号/文件哈希]
- 问题现象：[真实报错或异常现象]
- 主要提示内容：[粘贴或忠实摘录真实提示，不得事后虚构]
- AI 输出摘要：[忠实概括候选原因和建议]
- 完整交互记录位置：[支撑材料中的附件编号或导出文件名]

## 四、AI 输出的采纳、人工修改和核验情况

| 记录编号 | AI 建议 | 采纳情况 | 人工修改 | 核验方法 | 核验结果 |
|---|---|---|---|---|---|
| [D-01] | [真实建议摘要] | [采纳/部分采纳/未采纳] | [队员实际修改内容] | [测试命令、算例或人工审查方法] | [通过/未通过及关键结果] |

参赛队未直接复制未经检查的 AI 输出。所有采纳内容均由队员结合模型定义和程序上下文人工审查；修改后的程序通过[填写可复现的测试、基准比较、约束检查或结果一致性检查]核验。未采纳建议及其原因也保留在交互记录中。

## 五、完整性确认

经参赛队核对，本详情所列记录覆盖竞赛期间全部 AI 工具使用。除上述代码调试活动外，其他竞赛环节未使用 AI 工具。本说明中的工具、版本、时间、提示、采纳情况和核验结果均可由所附记录追溯。

参赛队员确认：[按赛事支撑材料要求填写或签署]
确认日期：[YYYY-MM-DD]
```

## Per-interaction ledger

Keep one row for every AI interaction, including both code debugging and framework assistance. Do not merge multiple sessions when their file versions, purposes, affected stages, adoption degrees, or outcomes differ.

```text
ID | timestamp | tool | version/model | code revision | error | prompt record |
AI output | adopted/partial/rejected | human edit | verification command | result
```

An example may explain the format but can never replace the team's real records.

## Code-debugging and framework-assistance report template

Use this branch when the phase matrix confirms AI use for code debugging and non-final framework assistance. Replace every bracketed field with verified facts and enumerate the affected stages instead of describing them as AI-free.

```markdown
# AI 工具使用详情

## 一、AI 工具基本信息

| 序号 | AI 工具名称 | 版本或模型 | 使用账号/访问方式 | 使用日期与时间范围 |
|---|---|---|---|---|
| 1 | [按日志填写工具名称] | [按界面或日志填写版本/模型] | [网页端/客户端/API/IDE 插件] | [YYYY-MM-DD HH:MM--HH:MM] |

## 二、具体使用目的和环节

本参赛队在代码调试及前期框架辅助环节使用了上述 AI 工具。代码调试用途包括[按真实记录填写错误分析、缺陷定位或测试建议]；前期框架辅助包括[逐项填写建模思路框架/代码模块骨架/数据处理流程框架/图表规划/论文结构草案等实际内容]。AI 输出仅作为非最终的结构性参考，不作为未经核验的模型结论、计算结果或论文定稿。

参赛队在此基础上独立完成了[模型选择与推导/算法重构/程序实现/数据计算/结果解释/图表定稿/论文改写]。各项 AI 输出的实际采纳程度、人工修改和核验方式见下文记录。

## 三、主要提示方式与使用过程

1. 队员记录待调试问题或需要梳理的初始框架目标，并保存当时的文件版本。
2. 向 AI 提交必要上下文，获取错误候选原因、检查清单、结构草案或模块骨架。
3. 队员逐项判断输出是否适用于赛题，记录“结构参考、部分采纳、完全替换或未采纳”。
4. 队员独立完成数学推导、代码重写、数据计算、图表制作和论文改写中的适用工作。
5. 通过版本差异、测试记录、约束检查、结果复算、图表来源和论文修订记录核验最终成果。

### 典型交互记录 [编号]

- 时间：[YYYY-MM-DD HH:MM]
- 工具及版本/模型：[按日志填写]
- 涉及环节：[代码调试/建模框架/代码骨架/数据流程/图表规划/论文结构]
- 主要提示内容：[粘贴或忠实摘录真实提示]
- AI 输出摘要：[忠实概括非最终建议或框架]
- 采纳程度：[结构参考/部分采纳/完全替换/未采纳]
- 完整交互记录位置：[附件编号或导出文件名]

## 四、AI 输出的采纳、人工修改和核验情况

| 记录编号 | AI 输出及用途 | 采纳程度 | 人工重构或修改 | 核验材料 | 核验结论 |
|---|---|---|---|---|---|
| [F-01] | [真实框架或调试建议摘要] | [结构参考/部分采纳/完全替换/未采纳] | [说明最终由队员完成的实质性工作] | [提交差异、推导记录、测试、复算或修订记录] | [通过/未通过及关键结果] |

AI 生成内容未被直接视为最终竞赛成果。核心模型和公式由队员结合赛题独立论证；程序由队员审查或重构并通过可复现测试；数据结果由实际运行产生并完成一致性检查；图表依据经核验数据重新制作；论文内容由队员结合最终模型、结果和证据进行实质性改写。仅填写真实发生且能够追溯的项目。

## 五、完整性确认

经参赛队核对，本详情覆盖竞赛期间全部 AI 工具使用。AI 工具主要用于代码调试及上述前期框架辅助，最终模型、程序、计算结果、图表和论文均经过队员的实质性重构、审查或核验。本说明中的工具、版本、时间、提示内容、采纳程度、人工修改和核验结果均可由所附记录追溯。

参赛队员确认：[按赛事支撑材料要求填写或签署]
确认日期：[YYYY-MM-DD]
```

## Final checks

- The compiled paper contains `AI 工具使用声明` immediately before references.
- The statement matches the evidence matrix and uses the official sentence.
- Every AI-used phase appears in the concise purpose text and the detail PDF.
- `AI 工具使用详情.pdf` exists for an AI-used declaration and opens successfully.
- The tool name and version/model are copied from evidence, not guessed.
- Typical interactions are genuine and traceable; secrets and personal data are redacted without changing substance.
- Each adopted debugging suggestion records the human edit and a reproducible verification result.
- Each framework-assistance record names the affected stage, adoption degree, substantive human reconstruction, and traceable verification evidence.
- No unresolved placeholders, `Unknown` phase statuses, or unsupported "未使用" claims remain.
