#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


BEGIN_ENV_RE = re.compile(r"\\begin\{(?P<name>[A-Za-z*]+)\}")
END_ENV_RE = re.compile(r"\\end\{(?P<name>[A-Za-z*]+)\}")
LABEL_RE = re.compile(r"\\label\{(?P<value>.*?)\}")
ROW_BREAK_RE = re.compile(r"(?<!\\)\\\\")
CONTROL_ROW_RE = re.compile(r"^\\(?:toprule|midrule|bottomrule|cmidrule|addlinespace)\b")
BOOKTABS_CMD_RE = re.compile(
    r"\\(?:toprule|midrule|bottomrule|addlinespace)\b|\\cmidrule(?:\([^)]*\))?\{[^{}]*\}",
    re.S,
)


def strip_comments(text: str) -> str:
    lines = []
    for line in text.splitlines():
        escaped = False
        out = []
        for ch in line:
            if ch == "%" and not escaped:
                break
            out.append(ch)
            escaped = ch == "\\"
        lines.append("".join(out))
    return "\n".join(lines)


def find_environment_blocks(text: str, env_name: str) -> list[str]:
    blocks: list[str] = []
    pos = 0
    begin_pat = re.compile(rf"\\begin\{{{re.escape(env_name)}\}}(?:\[[^\]]*\])?")

    while True:
        match = begin_pat.search(text, pos)
        if not match:
            return blocks

        depth = 1
        cursor = match.end()
        while depth > 0:
            begin = BEGIN_ENV_RE.search(text, cursor)
            end = END_ENV_RE.search(text, cursor)
            if end is None:
                raise ValueError(f"Unclosed environment: {env_name}")
            if begin and begin.start() < end.start():
                if begin.group("name") == env_name:
                    depth += 1
                cursor = begin.end()
            else:
                if end.group("name") == env_name:
                    depth -= 1
                cursor = end.end()

        blocks.append(text[match.start():cursor])
        pos = cursor


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def find_matching_brace(text: str, open_index: int) -> int:
    depth = 0
    for index in range(open_index, len(text)):
        ch = text[index]
        if ch == "{" and (index == 0 or text[index - 1] != "\\"):
            depth += 1
        elif ch == "}" and (index == 0 or text[index - 1] != "\\"):
            depth -= 1
            if depth == 0:
                return index
    raise ValueError("Unmatched brace in TeX source")


def extract_braced(text: str, open_index: int) -> tuple[str, int]:
    close_index = find_matching_brace(text, open_index)
    return text[open_index + 1:close_index], close_index + 1


def extract_command_argument(block: str, command: str) -> str:
    command_index = block.find(command)
    if command_index == -1:
        return ""

    cursor = command_index + len(command)
    while cursor < len(block) and block[cursor].isspace():
        cursor += 1

    if cursor < len(block) and block[cursor] == "[":
        optional_end = block.find("]", cursor)
        if optional_end == -1:
            return ""
        cursor = optional_end + 1
        while cursor < len(block) and block[cursor].isspace():
            cursor += 1

    if cursor >= len(block) or block[cursor] != "{":
        return ""

    value, _ = extract_braced(block, cursor)
    return normalize_whitespace(value)


def find_tabular_start(block: str) -> tuple[str, int] | None:
    for env in ("tabularx", "tabular"):
        token = f"\\begin{{{env}}}"
        start = block.find(token)
        if start != -1:
            return env, start + len(token)
    return None


def extract_tabular_info(block: str) -> dict[str, object] | None:
    start_info = find_tabular_start(block)
    if not start_info:
        return None

    env, cursor = start_info
    while cursor < len(block) and block[cursor].isspace():
        cursor += 1

    width = ""
    if env == "tabularx":
        if cursor >= len(block) or block[cursor] != "{":
            raise ValueError("tabularx is missing width argument")
        width, cursor = extract_braced(block, cursor)
        while cursor < len(block) and block[cursor].isspace():
            cursor += 1

    if cursor >= len(block) or block[cursor] != "{":
        raise ValueError(f"{env} is missing column specification")
    spec, cursor = extract_braced(block, cursor)

    end_tag = rf"\\end\{{{env}\}}"
    end = re.search(end_tag, block[cursor:], re.S)
    if not end:
        return {
            "environment": env,
            "width": normalize_whitespace(width or ""),
            "column_spec": normalize_whitespace(spec or ""),
            "raw_rows": [],
            "display_rows": [],
        }

    body = block[cursor: cursor + end.start()]
    cleaned_body = BOOKTABS_CMD_RE.sub("\n", body)
    rows = []
    display_rows = []
    for row in ROW_BREAK_RE.split(cleaned_body):
        line = normalize_whitespace(row)
        if not line or CONTROL_ROW_RE.match(line):
            continue
        rows.append(line)
        display_rows.append(re.sub(r"\s*&\s*", " | ", line))

    return {
        "environment": env,
        "width": normalize_whitespace(width or ""),
        "column_spec": normalize_whitespace(spec or ""),
        "raw_rows": rows,
        "display_rows": display_rows,
    }


def build_context(tex_path: Path) -> dict[str, object]:
    raw_text = tex_path.read_text(encoding="utf-8")
    text = strip_comments(raw_text)
    blocks = find_environment_blocks(text, "LabRecordTable")

    tables = []
    for index, block in enumerate(blocks, start=1):
        tabular_info = extract_tabular_info(block)
        tables.append(
            {
                "index": index,
                "caption": extract_command_argument(block, r"\caption"),
                "label": normalize_whitespace(LABEL_RE.search(block).group("value")) if LABEL_RE.search(block) else "",
                "tabular": tabular_info,
                "raw_block": block.strip(),
            }
        )

    return {
        "source_tex": str(tex_path),
        "table_count": len(tables),
        "tables": tables,
    }


def resolve_tex_path(arg: str) -> Path:
    path = Path(arg)
    if path.is_dir():
        path = path / "main.tex"
    if not path.exists():
        raise FileNotFoundError(f"Cannot find TeX source: {path}")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract LabRecordTable context from a report TeX file."
    )
    parser.add_argument("target", help="Experiment directory or main.tex path")
    parser.add_argument(
        "-o",
        "--output",
        help="Write JSON output to this path instead of stdout",
    )
    args = parser.parse_args()

    tex_path = resolve_tex_path(args.target)
    context = build_context(tex_path)
    rendered = json.dumps(context, ensure_ascii=False, indent=2) + "\n"

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
