#!/usr/bin/env python3
"""Apply the fenced-code treatment to quiz `explanation` fields.

Prompts were already moved to the fenced shape by refactor_prompt_code.py
(single span) and restructure_multispan.py (multi span):

    کد زیر را در نظر بگیرید:
    ```java
    <code>
    ```
    <sentence referencing «کد بالا»>

Explanations are prose, so the fence is NOT hoisted to the front: each
extractable code span is replaced IN PLACE by the lead-in, a ```java fence
carrying the code, and the referent «کد بالا», keeping the surrounding
Persian sentence exactly where it was:

    شکل `new int[]{...}` آرایهٔ بی‌نام می‌سازد...
    →  شکل کد زیر را در نظر بگیرید:
       ```java
       new int[]{...}
       ```
       کد بالا آرایهٔ بی‌نام می‌سازد...

Recipe (same is_code predicate as the prompt sweeps):

- A span is SHORT (<= 6 chars: `f(0)`, `==`, `x++`) when len(span) <= 6;
  short spans read fine inline and stay untouched.
- Consecutive extractable spans separated only by Persian joiner words
  (، و یا با) collapse into ONE fence with one line per span and a single
  «کد بالا» — an enumeration must not be pulled apart.
- Otherwise each qualifying span (or run) becomes its own fence at its
  original position, each hole filled by «کد بالا». When two fences would
  land too close together (fewer than MIN_GAP_WORDS words of prose between
  the spans) the explanation is skipped for review rather than mangled.
- Explanations that are mostly code (no Persian letters at all) or already
  fenced are skipped.

Only q["explanation"] is modified; ids, prompts, answers, options and key
order are preserved. The same deterministic transform runs on the published
banks and on .parts sources so future merges reproduce identical output.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPAN = re.compile(r"`([^`\n]+)`")

STRONG = (";", "=", "(", ")", "{", "}", "[", "]", ":", "...", "->", "<<", ">>", ">>>", "&&", "||", "++", "--", "=>")
OPERATOR = re.compile(r"[+\-*/%<>!&|^]")
PERSIAN = re.compile(r"[؀-ۿݐ-ݿࢠ-ࣿﭐ-﷿ﹰ-﻿]")
ZWNJ = chr(0x200C)

LEAD_IN = "کد زیر را در نظر بگیرید:"
REFERENCE = "کد بالا"
JOINERS = {"،", "و", "یا", "با"}
SHORT_LIMIT = 6
MIN_GAP_WORDS = 3  # prose words required between two separate fences


def is_code(span: str) -> bool:
    if any(tok in span for tok in STRONG):
        return True
    if OPERATOR.search(span) and " " in span:
        return True
    return False


def is_long(span: str) -> bool:
    return len(span) > SHORT_LIMIT


def pure_joiner(text: str) -> bool:
    """True when text between two spans is only whitespace/joiner words."""
    tokens = text.replace(ZWNJ, " ").split()
    return bool(tokens) and all(tok in JOINERS for tok in tokens)


def word_count(text: str) -> int:
    return len(text.replace(ZWNJ, " ").split())


def fence(lines: list[str]) -> str:
    return f"{LEAD_IN}\n\n```java\n" + "\n".join(lines) + "\n```\n\n"


def transform_explanation(exp: str):
    """Return (new_explanation, None) or (None, reason)."""
    if "```" in exp:
        return None, "fenced"
    if "`" not in exp:
        return None, "nocode"
    if not PERSIAN.search(exp):
        return None, "nocode"  # mostly code, no Persian prose to anchor a fence

    matches = [m for m in SPAN.finditer(exp) if is_code(m.group(1))]
    if not matches:
        return None, "nocode"  # only identifier-like spans; fine inline

    runs = [[matches[0]]]
    for m in matches[1:]:
        gap = exp[runs[-1][-1].end():m.start()]
        if pure_joiner(gap):
            runs[-1].append(m)  # enumeration: one fence, single referent
        elif word_count(gap) < MIN_GAP_WORDS:
            return None, "close"  # fences would land too close; leave for review
        else:
            runs.append([m])

    holes = []  # (start, end, replacement)
    for run in runs:
        if not any(is_long(m.group(1)) for m in run):
            continue  # isolated short span(s): read fine inline
        start, end = run[0].start(), run[-1].end()
        repl = fence([m.group(1) for m in run]) + REFERENCE
        if start > 0 and exp[start - 1] not in " \n":
            repl = " " + repl
        if end < len(exp) and exp[end] not in " \n،؛.؟!:»«)]":
            repl += " "
        holes.append((start, end, repl))
    if not holes:
        return None, "short"  # every extractable span is short; fine inline

    out = exp
    for start, end, repl in reversed(holes):
        out = out[:start] + repl + out[end:]
    return out, None


def process_file(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    stats = {
        "file": str(path.relative_to(ROOT)),
        "restructured": 0,
        "skipped_short": 0,
        "skipped_close": 0,
    }
    for q in data.get("questions", []):
        exp = q.get("explanation")
        if not isinstance(exp, str):
            continue
        new, reason = transform_explanation(exp)
        if new is not None:
            q["explanation"] = new
            stats["restructured"] += 1
        elif reason == "short":
            stats["skipped_short"] += 1
        elif reason == "close":
            stats["skipped_close"] += 1
    out = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    if out != raw:
        path.write_text(out, encoding="utf-8")
    return stats


def main() -> int:
    files = sorted((ROOT / "book" / "quiz").glob("grade-*.json")) + sorted(
        (ROOT / "book" / "quiz" / ".parts").glob("*.json")
    )
    tot_r = tot_s = tot_c = 0
    for f in files:
        s = process_file(f)
        tot_r += s["restructured"]
        tot_s += s["skipped_short"]
        tot_c += s["skipped_close"]
        if s["restructured"] or s["skipped_short"] or s["skipped_close"]:
            print(
                f"{s['file']}: {s['restructured']} restructured, "
                f"{s['skipped_short']} skipped-short, {s['skipped_close']} skipped-close"
            )
    print(f"\nTOTAL: {tot_r} restructured, {tot_s} skipped-short, {tot_c} skipped-close")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
