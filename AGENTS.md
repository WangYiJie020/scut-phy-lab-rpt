# Repository Guidelines

## Project Structure & Module Organization
This repository contains LaTeX sources for physics lab coursework. Source files now live under `src/`, with each experiment report in its own directory and a `main.tex` entrypoint, for example `src/绪论/main.tex` and `src/exp8-分光计/main.tex`. Experiment-specific figures live under each report’s `assets/` folder. Shared report infrastructure is under `src/template/`, especially `src/template/myrpt.cls`, `src/template/封面.pdf`, and the bundled PDF assets.

## Build, Test, and Development Commands
Use XeLaTeX because the documents depend on `xeCJK` and `ctex`.

```sh
make
make 绪论
make exp1-弗朗克
make exp1-电子逸出功
make clean
make distclean
```

The root `Makefile` uses XeLaTeX to compile every report directory under `src/` with a `main.tex` entrypoint, excluding `src/template/`. Final PDFs are written to `output/` and named after their directory, for example `output/exp1-弗朗克.pdf`. Intermediate files such as `*.aux`, `*.log`, and `*.out` are written under `build/`. The Makefile tracks dependencies and skips recompilation when sources are unchanged.

## Coding Style & Naming Conventions
Keep LaTeX source readable and consistent with the existing files: 2-space indentation inside environments, one sentence or command block per line when practical, and aligned table rows for dense tabular data. Preserve the current naming pattern: report directories under `src/` use `main.tex` as the entry file, and image assets stay in the local `assets/` directory beside the document that uses them. Reuse `src/template/myrpt.cls` instead of redefining layout macros in each report. From `exp8-分光计` onward, start the document with `\insertCoverPage` and still call `\maketitle` after the cover. The cover carries the experiment name and student information; `\maketitle` remains the in-text title block.

## Experiment Workflow
Each experiment report is completed in two stages.

1. Preparation stage: generate the report framework without measured data or data analysis.
2. Completion stage: after the user provides reviewed data, fill in the tables, replace the raw-record appendix, and finish the analysis.

From `exp8-分光计` onward, reports use `\insertCoverPage` and still call `\maketitle`. The cover fills 课程名称 / 姓名 / 学号 / 专业班级 / 开课学期 from the class macros (`\ExamName`, `\StuName`, `\StuID`, `\StuClass`, `\ClassPeriod`). The running header is two-sided: even pages show `大学物理实验报告` on the left, odd pages show `\ExamName(第\ExamIdx次实验)` on the right. Override the index with `\ExamIdx{n}` (default `0`). The cover and the following blank page are unnumbered. `\insertSignedDataPage` starts the signed raw-record appendix on an odd page, inserting an intentionally blank page if needed.

During the preparation stage:

- If `src/xxx/ref/` contains multiple reference files, treat the file whose name contains `模板` as the teacher-provided template and use it as the primary reference during drafting.
- If `src/xxx/ref/` contains reference answer documents but no file name contains `模板`, follow the most relevant reference document's format and content first when drafting the report `tex` file.
- Extract images and similar assets used by the primary reference Word document into `src/xxx/assets/` when possible so the `tex` file can reference them directly. If extraction fails, tell the user so they can help provide the assets.
- Use three-line tables for report tables.
- Any table intended for later handwritten or measured lab data must use the `LabRecordTable` environment.
- Keep table headers on one line when possible; if a header is too long, adjust column widths instead of letting the header wrap badly.
- If the template document does not provide any thought questions, do not add thought-question sections or placeholder answers in the preparation-stage `tex` draft.
- At the end of the draft report, use `\insertRawDataPage` so the raw-data appendix is auto-generated from the `LabRecordTable` contents.

During the completion stage:

- The user will update experiment data under `src/xxx/data/`.
- The user will also provide the teacher-signed raw record image at `src/xxx/data/signed_RawRecord.jpg`.
- If measured data needs to be extracted from `src/xxx/data/signed_RawRecord.jpg`, read the corresponding `src/xxx/main.tex` first and use every `LabRecordTable` in that file as the primary reference for the expected table structure, headers, units, fixed printed text, and intentionally blank regions.
- Do not assume signed raw-record tables share one fixed layout across experiments; interpret each image against its own report `tex` file instead of reusing another experiment’s table pattern.
- Treat image recognition as a guided extraction task: compare the image against the referenced `LabRecordTable` definition and flag uncertain or structurally conflicting cells for review instead of silently guessing values.
- If helpful, extract `LabRecordTable` context into a temporary or structured helper file under `src/xxx/data/` or `build/`, but avoid coupling the workflow to unstable template internals in `src/template/myrpt.cls`.
- After extracting measured data from `signed_RawRecord.jpg`, show the extracted results to the user and explicitly ask whether any corrections are needed before treating the values as final.
- Do not fill extracted values back into the report or continue the analysis until the user has either confirmed the data or provided corrections.
- If you write helper scripts for data extraction or data processing during this stage, keep them as reproducible artifacts inside the experiment directory, preferably under `src/xxx/data/`, instead of leaving the workflow only in transient shell history.
- Replace the draft-stage `\insertRawDataPage` call with `\insertSignedDataPage`.
- `\insertSignedDataPage` is the standard way to insert the signed raw-record scan; do not manually recreate that page layout in each report unless there is a specific exception.
- Fill the measured data back into the tables in the `tex` source.
- Then read `src/xxx/ref/*.docx` and complete the missing data-analysis sections in the report.
- In `数据处理`, each measurement item must include both 误差分析 and 不确定度分析: compare the result with the accepted or expected value, identify systematic versus random sources specific to that measurement, propagate Type B (and Type A if repeated) uncertainties, and report the result with uncertainty.
- After data processing, add a `\section{实验的分析和总结}` that interprets the results, classifies overall error sources, and states whether the experiment objectives were met. Do not fold this into a short remark at the end of `数据处理`.
- If extra tooling is needed to inspect or extract content from a `.docx` file, ask the user before installing it.

## Testing Guidelines
There is no automated test suite. The required check is successful compilation of every modified `.tex` entry file with XeLaTeX and a quick PDF review for broken figure paths, unresolved references, table overflow, and raw-data appendix placement. If you edit `src/template/myrpt.cls`, recompile at least one experiment report and one standalone file such as `src/绪论/main.tex`.

## Commit & Pull Request Guidelines
Follow the existing commit style: short, imperative summaries such as `add .gitignore` or `init with exp1 and 绪论`. Keep each commit scoped to one logical change. Pull requests should state which reports or template files changed, note the compile commands you ran, and include screenshots only when layout changes are hard to describe in text.
