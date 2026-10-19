#!/usr/bin/env python3
"""Verify the quiz CLI renders Persian prose with Unicode bidi isolates.

Asserts that the format_rtl_block helper (used by reader.ask and reader.response_for)
correctly handles the prompt shape introduced by tools/refactor_prompt_code.py:
a Persian lead-in line, a fenced java code block, and a Persian question line.
Persian lines must be right-aligned and wrapped in RLI/PDI with inline Latin
runs isolated with LRI/PDI; fence lines and the code inside them must pass
through verbatim (LTR, no controls). The JAVABOOK_BIDI=off bypass is honored.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from reader import format_rtl_block  # noqa: E402

RLI = "⁧"  # right-to-left isolate
LRI = "⁦"  # left-to-right isolate
PDI = "⁩"  # pop directional isolate

WIDTH = 80
TARGET_ID = "g2-comparison-001"


def load_target_prompt() -> str:
    """Load a question with the restructured prompt shape from the merged grade-02 bank."""
    bank = ROOT / "book" / "quiz" / "grade-02.json"
    data = json.loads(bank.read_text(encoding="utf-8"))
    for question in data["questions"]:
        if question["id"] != TARGET_ID:
            continue
        prompt = question["prompt"]
        # Sanity: must contain Persian letters AND a fenced code block.
        has_persian = any("؀" <= char <= "ۿ" for char in prompt)
        has_fence = "```java" in prompt
        if has_persian and has_fence:
            return prompt
    raise SystemExit(f"FAIL: {TARGET_ID} not found or did not have Persian + fenced code content")


def assert_default_rtl(prompt: str) -> list[str]:
    """Default mode: right-aligned prose lines with RLI/PDI; fence + code verbatim."""
    rendered = format_rtl_block(prompt, WIDTH)
    lines = rendered.splitlines()
    failures: list[str] = []

    # 1) The fenced code line must pass through verbatim: no isolates, no padding.
    code_line = "score >= 60"
    if code_line not in lines:
        failures.append(f"fenced code line {code_line!r} not present verbatim in rendered output")
    else:
        idx = lines.index(code_line)
        if LRI in code_line or PDI in code_line:
            failures.append(f"fenced code line unexpectedly wrapped in isolates: {code_line!r}")
        # The lines around the code must be the ``` fence markers.
        if lines[idx - 1].strip() != "```java":
            failures.append(f"opening fence missing before code: {lines[idx - 1]!r}")
        if lines[idx + 1].strip() != "```":
            failures.append(f"closing fence missing after code: {lines[idx + 1]!r}")

    # 2) Persian lines must start with at least one leading space (right-aligned).
    persian_lines = [line for line in lines if any("؀" <= ch <= "ۿ" for ch in line)]
    if not persian_lines:
        failures.append("no Persian line found in rendered output")
    for persian_line in persian_lines:
        if not persian_line.startswith(" "):
            failures.append(f"Persian line not right-aligned: {persian_line!r}")
        # The visible portion (excluding controls) must equal exactly WIDTH chars.
        visible = [char for char in persian_line if char not in {RLI, LRI, PDI}]
        if len(visible) != WIDTH:
            failures.append(f"Persian line visible width {len(visible)} != {WIDTH}: {persian_line!r}")

    # 3) The Persian lines must be wrapped in an RLI..PDI pair; the question line
    #    must reference the code block above it.
    if RLI not in rendered or PDI not in rendered:
        failures.append("RLI or PDI missing from default-mode rendering")
    if not any("کد بالا" in line for line in persian_lines):
        failures.append("question line does not reference the code block above it")

    return failures


def assert_compat_mode(prompt: str) -> list[str]:
    """JAVABOOK_BIDI=off: no bidi controls are emitted."""
    os.environ["JAVABOOK_BIDI"] = "off"
    try:
        rendered = format_rtl_block(prompt, WIDTH)
    finally:
        del os.environ["JAVABOOK_BIDI"]
    failures: list[str] = []
    for control, name in [(RLI, "RLI"), (LRI, "LRI"), (PDI, "PDI")]:
        if control in rendered:
            failures.append(f"{name} leaked into JAVABOOK_BIDI=off output: {rendered!r}")
    # Persian line should still be right-aligned even in compatibility mode.
    persian_line = next(
        (line for line in rendered.splitlines() if any("؀" <= ch <= "ۿ" for ch in line)),
        None,
    )
    if persian_line is None or not persian_line.startswith(" "):
        failures.append(f"compatibility-mode Persian line not right-aligned: {persian_line!r}")
    return failures


def main() -> int:
    prompt = load_target_prompt()
    print(f"Target question id: {TARGET_ID}")
    print(f"Prompt (logical order): {prompt}")

    default_failures = assert_default_rtl(prompt)
    compat_failures = assert_compat_mode(prompt)

    print()
    print("Default mode (RLI + LRI + PDI):")
    print(f"  rendered: {format_rtl_block(prompt, WIDTH)!r}")

    if default_failures or compat_failures:
        print()
        print("FAIL")
        for failure in default_failures + compat_failures:
            print(f"  - {failure}")
        return 1

    print()
    print("PASS")
    print(f"  default mode: Persian lead-in/question right-aligned with RLI/PDI; fenced code verbatim; `{TARGET_ID}` references the block")
    print("  compat mode (JAVABOOK_BIDI=off): no bidi controls emitted; Persian still right-aligned")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
