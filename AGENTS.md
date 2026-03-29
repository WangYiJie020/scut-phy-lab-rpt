# Repository Guidelines

## Project Structure & Module Organization
This repository contains LaTeX sources for physics lab coursework. Source files now live under `src/`, with report entrypoints at `src/绪论/main.tex`, `src/exp1-弗朗克/main.tex`, and `src/exp1-电子逸出功/main.tex`. Experiment-specific figures live under each report’s `assets/` folder. Shared report infrastructure is under `src/template/`, especially `src/template/myrpt.cls` and the bundled PDF assets.

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
Keep LaTeX source readable and consistent with the existing files: 2-space indentation inside environments, one sentence or command block per line when practical, and aligned table rows for dense tabular data. Preserve the current naming pattern: report directories under `src/` use `main.tex` as the entry file, and image assets stay in the local `assets/` directory beside the document that uses them. Reuse `src/template/myrpt.cls` instead of redefining layout macros in each report.

## Testing Guidelines
There is no automated test suite. The required check is successful compilation of every modified `.tex` entry file with XeLaTeX and a quick PDF review for broken figure paths, unresolved references, table overflow, and raw-data appendix placement. If you edit `src/template/myrpt.cls`, recompile at least one experiment report and one standalone file such as `src/绪论/main.tex`.

## Commit & Pull Request Guidelines
Follow the existing commit style: short, imperative summaries such as `add .gitignore` or `init with exp1 and 绪论`. Keep each commit scoped to one logical change. Pull requests should state which reports or template files changed, note the compile commands you ran, and include screenshots only when layout changes are hard to describe in text.
