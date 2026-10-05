#!/usr/bin/env python3
"""Compile and run explicitly marked Java examples in a book chapter.

Markers are documented in book/02-operators-control-flow.md:
<!-- verify: run id=unique-id -->
<!-- verify: compile-fail id=unique-id -->
<!-- verify: skip id=unique-id -->
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKER = re.compile(r"<!--\s*verify:\s*(run|compile-fail|skip)\s+id=(?![\.]+)([\w.-]+)(?:\s+[^>]*)?\s*-->")
JAVA_FENCE = re.compile(r"```java\s*\n(.*?)\n```", re.DOTALL)
TEXT_FENCE = re.compile(r"خروجی:\s*\n```text\s*\n(.*?)\n```", re.DOTALL)
PUBLIC_CLASS = re.compile(r"\bpublic\s+class\s+(\w+)")
CLASS = re.compile(r"\bclass\s+(\w+)")


@dataclass(frozen=True)
class Example:
    mode: str
    identifier: str
    source: str
    expected: str | None


def normalize(value: str) -> str:
    lines = [line.rstrip() for line in value.strip().splitlines()]
    compact: list[str] = []
    blank = False
    for line in lines:
        if line:
            compact.append(line)
            blank = False
        elif not blank:
            compact.append("")
            blank = True
    return "\n".join(compact).strip()


def chapter_path(number: int) -> Path:
    matches = sorted((ROOT / "book").glob(f"{number:02d}-*.md"))
    if len(matches) != 1:
        raise ValueError(f"expected exactly one chapter for {number}; found {len(matches)}")
    return matches[0]


def examples_from(chapter: Path) -> list[Example]:
    text = chapter.read_text(encoding="utf-8")
    examples: list[Example] = []
    for marker in MARKER.finditer(text):
        fence = JAVA_FENCE.search(text, marker.end())
        next_marker = MARKER.search(text, marker.end())
        if fence is None or (next_marker is not None and next_marker.start() < fence.start()):
            raise ValueError(f"{chapter}: marker {marker.group(2)} has no following Java fence")
        between = text[fence.end():next_marker.start() if next_marker else len(text)]
        output = TEXT_FENCE.search(between)
        expected = output.group(1) if output else None
        if marker.group(1) == "run" and expected is None:
            raise ValueError(f"{chapter}: runnable {marker.group(2)} has no adjacent خروجی text fence")
        examples.append(Example(marker.group(1), marker.group(2), fence.group(1), expected))
    if not examples:
        raise ValueError(f"{chapter}: no verification markers found")
    return examples


def class_name(source: str, identifier: str) -> str:
    public_match = PUBLIC_CLASS.search(source)
    if public_match:
        return public_match.group(1)
    class_match = CLASS.search(source)
    if class_match:
        return class_match.group(1)
    raise ValueError(f"{identifier}: no top-level class found; mark this fragment skip")


def execute(example: Example) -> tuple[bool, str]:
    try:
        name = class_name(example.source, example.identifier)
    except ValueError as error:
        return False, str(error)
    with tempfile.TemporaryDirectory(prefix="java-book-example-") as directory:
        workspace = Path(directory)
        source_file = workspace / f"{name}.java"
        source_file.write_text(example.source + "\n", encoding="utf-8")
        compiled = subprocess.run(
            ["javac", "--release", "21", source_file.name],
            cwd=workspace, text=True, capture_output=True, check=False,
        )
        if example.mode == "compile-fail":
            if compiled.returncode != 0:
                return True, "compile failure observed"
            return False, "compiled successfully but compile failure was expected"
        if compiled.returncode != 0:
            return False, "javac failed:\n" + compiled.stderr.strip()
        ran = subprocess.run(
            ["java", "-cp", str(workspace), name],
            cwd=workspace, text=True, capture_output=True, check=False,
        )
        if ran.returncode != 0:
            return False, "java failed:\n" + ran.stderr.strip()
        actual = normalize(ran.stdout)
        expected = normalize(example.expected or "")
        if actual != expected:
            return False, f"output mismatch\nexpected: {expected!r}\nactual:   {actual!r}"
        return True, "output matched"


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify marked Java examples in a chapter")
    parser.add_argument("--chapter", required=True, type=int, help="numeric chapter, for example 2")
    args = parser.parse_args()
    if shutil.which("javac") is None or shutil.which("java") is None:
        print("ERROR: java and javac must be on PATH", file=sys.stderr)
        return 2
    try:
        chapter = chapter_path(args.chapter)
        examples = examples_from(chapter)
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    passed = failed = skipped = 0
    for example in examples:
        if example.mode == "skip":
            skipped += 1
            print(f"SKIP {example.identifier}: explicitly non-runnable")
            continue
        ok, detail = execute(example)
        if ok:
            passed += 1
            print(f"PASS {example.identifier}: {detail}")
        else:
            failed += 1
            print(f"FAIL {example.identifier}: {detail}", file=sys.stderr)
    print(f"SUMMARY: passed={passed} failed={failed} skipped={skipped} total={len(examples)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
