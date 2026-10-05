#!/usr/bin/env python3
"""Verify the quiz CLI renders Persian prose with Unicode bidi isolates.

Asserts that the format_rtl_block helper (used by reader.ask and reader.response_for)
correctly wraps Persian prose with RLI/PDI and protects embedded English/code/number
runs with LRI/PDI, while leaving the JAVABOOK_BIDI=off bypass honored.
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
    """Load a known mixed-bidi question prompt from the merged grade-02 bank."""
    bank = ROOT / "book" / "quiz" / "grade-02.json"
    data = json.loads(bank.read_text(encoding="utf-8"))
    for question in data["questions"]:
        if question["id"] != TARGET_ID:
            continue
        prompt = question["prompt"]
        # Sanity: must contain Persian letters AND an inline backtick run.
        has_persian = any("؀" <= char <= "ۿ" for char in prompt)
        has_backtick_run = "`" in prompt
        if has_persian and has_backtick_run:
            return prompt
    raise SystemExit(f"FAIL: {TARGET_ID} not found or did not have Persian + inline backtick content")


def assert_default_rtl(prompt: str) -> list[str]:
    """Default mode: right-aligned + isolates wrap prose and protect inline runs."""
    rendered = format_rtl_block(prompt, WIDTH)
    lines = rendered.splitlines()
    failures: list[str] = []

    # 1) Inline backtick run `score >= 60` must be wrapped by LRI..PDI.
    inline_run = "`score >= 60`"
    if inline_run not in rendered:
        failures.append(f"inline backtick run {inline_run!r} missing from rendered output")
    else:
        idx = rendered.find(inline_run)
        # The character immediately before the backtick must be LRI; the char
        # immediately after the closing backtick must be PDI.
        if idx == 0 or rendered[idx - 1] != LRI:
            failures.append(f"LRI missing directly before {inline_run!r}")
        if rendered[idx + len(inline_run)] != PDI:
            failures.append(f"PDI missing directly after {inline_run!r}")

    # 2) The Persian line must start with at least one leading space (right-aligned).
    persian_line = next((line for line in lines if any("؀" <= ch <= "ۿ" for ch in line)), None)
    if persian_line is None:
        failures.append("no Persian line found in rendered output")
    else:
        if not persian_line.startswith(" "):
            failures.append(f"Persian line not right-aligned: {persian_line!r}")
        # The visible portion (excluding controls) must equal exactly WIDTH chars.
        visible = [char for char in persian_line if char not in {RLI, LRI, PDI}]
        if len(visible) != WIDTH:
            failures.append(f"Persian line visible width {len(visible)} != {WIDTH}: {persian_line!r}")

    # 3) The Persian line must contain an RLI..PDI pair wrapping the prose.
    if RLI not in rendered or PDI not in rendered:
        failures.append("RLI or PDI missing from default-mode rendering")

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
    print(f"  default mode: LRI/PDI wrap `{TARGET_ID}`'s `score >= 60`; Persian prose right-aligned; RLI present")
    print("  compat mode (JAVABOOK_BIDI=off): no bidi controls emitted; Persian still right-aligned")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
