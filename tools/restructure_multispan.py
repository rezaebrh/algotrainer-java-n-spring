#!/usr/bin/env python3
"""Restructure quiz prompts that still weave code spans into Persian prose.

The single-span sweep (refactor_prompt_code.py) already moved prompts with
exactly one extractable span into the fenced shape:

    کد زیر را در نظر بگیرید:
    ```java
    <code>
    ```
    <question referencing «کد بالا»>

What remains are prompts with TWO OR MORE extractable spans (signature and
expression enumerations woven into the sentence) plus hand-authored multiline
prompts (a question line followed by a bare `code` line, sometimes a span that
itself crosses lines). Recipe:

- Collect all extractable spans in order (same is_code predicate as before).
- If every extractable span is SHORT (<= 6 chars, e.g. `f(0)`, `a[2]`, `==`):
  skip — short spans read acceptably inline.
- Otherwise build one ```java block from the extracted spans, one per line.
- Spans are grouped into RUNS: consecutive extractable spans whose separating
  text is nothing but whitespace and/or Persian joiner words (، و یا با)
  collapse into one run (an enumeration). A run is extracted when it contains
  at least one long span; when a run mixes short and long spans the whole run
  moves into the block — pulling only the long half of "`f(0)` و `f(0L)` و
  `f(0.0)`" apart would break the parallel list. Isolated all-short runs stay
  inline.
- A stripped run leaves a hole. When the hole covers an entire line (a bare
  code line) that line is dropped; otherwise the hole is filled with «کد
  بالا» (single span) or «کدهای بالا» (two or more).
- Non-code spans (bare identifiers like `switch`) stay inline untouched.
- Multiline prompts (no fence): same recipe over the whole prompt; surviving
  question lines land after the fence. Stale «کد زیر» references inside the
  sentence are rewritten to «کد بالا».

Only q["prompt"] is modified; ids, answers, options, explanations and key order
are preserved. Output is written with json.dumps(..., ensure_ascii=False,
indent=2) + "\n". The same deterministic transform runs on the published banks
and on .parts sources (including the grades-*-seeds.json files) so future
merges reproduce identical prompts.
"""
import argparse
import json
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPAN = re.compile(r"`([^`]+)`")  # spans may cross lines in hand-authored prompts

STRONG = (";", "=", "(", ")", "{", "}", "[", "]", ":", "...", "->", "<<", ">>", ">>>", "&&", "||", "++", "--", "=>")
OPERATOR = re.compile(r"[+\-*/%<>!&|^]")
ZWNJ = chr(0x200c)

LEAD_IN = "کد زیر را در نظر بگیرید:"
REF_SINGLE = "کد بالا"      # hole that absorbed exactly one span
REF_PLURAL = "کدهای بالا"   # hole that absorbed two or more spans
STALE_BELOW = "کد زیر"
JOINERS = {"،", "و", "یا", "با"}
SHORT_LIMIT = 6


def is_long(span: str) -> bool:
    return "\n" in span or len(span) > SHORT_LIMIT


def is_code(span: str) -> bool:
    if any(tok in span for tok in STRONG):
        return True
    if OPERATOR.search(span) and " " in span:
        return True
    return False


def pure_joiner(text: str) -> bool:
    """True when text between two spans is only whitespace/joiner words."""
    tokens = text.replace(ZWNJ, " ").split()
    return all(tok in JOINERS for tok in tokens)


def line_exclusive(prompt: str, start: int, end: int) -> bool:
    """True when [start, end) is the only non-space content of its line(s)."""
    line_start = prompt.rfind("\n", 0, start) + 1
    line_end = prompt.find("\n", end)
    if line_end == -1:
        line_end = len(prompt)
    before = prompt[line_start:start]
    after = prompt[end:line_end]
    return before.strip() == "" and after.strip() == ""


def transform_prompt(prompt: str):
    """Return (new_prompt, None) or (None, reason) with reason in
    {"short", "other", "fenced", "nocode"}."""
    if "```" in prompt:
        return None, "fenced"
    if "`" not in prompt:
        return None, "nocode"

    matches = [m for m in SPAN.finditer(prompt) if is_code(m.group(1))]
    if not matches:
        return None, "nocode"  # only identifier-like spans; fine inline
    multiline = "\n" in prompt
    if not multiline and len(matches) < 2:
        return None, "other"  # single-span single-line: previous sweep's scope

    runs = [[matches[0]]]
    for m in matches[1:]:
        if pure_joiner(prompt[runs[-1][-1].end():m.start()]):
            runs[-1].append(m)
        else:
            runs.append([m])

    holes = []  # (start, end, replacement)
    code = []
    for run in runs:
        if not any(is_long(m.group(1)) for m in run):
            continue  # isolated short span(s): read fine inline
        code.extend(m.group(1) for m in run)
        start, end = run[0].start(), run[-1].end()
        if line_exclusive(prompt, start, end):
            repl = ""  # bare code line: drop it rather than leave a referent
        else:
            repl = REF_SINGLE if len(run) == 1 else REF_PLURAL
        holes.append((start, end, repl))
    if not code:
        return None, "short"  # every extractable span is short; fine inline

    out = prompt
    for start, end, repl in reversed(holes):
        out = out[:start] + repl + out[end:]

    kept = []
    for line in out.split("\n"):
        line = re.sub(r"[ \t]+", " ", line)
        line = re.sub(r" +([،؛؟!])", r"\1", line)
        line = re.sub(r"^[،؛]\s*", "", line).strip()
        if line:
            kept.append(line)
    sentence = "\n".join(kept).replace(STALE_BELOW, REF_SINGLE)
    if not sentence:
        return None, "other"  # degenerate: prompt was nothing but code spans

    block = "\n".join(code)
    return f"{LEAD_IN}\n\n```java\n{block}\n```\n\n{sentence}", None


def process_file(path: Path, samples: list) -> dict:
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    stats = {
        "file": str(path.relative_to(ROOT)),
        "restructured": 0,
        "skipped_short": 0,
        "skipped_other": 0,
    }
    for q in data.get("questions", []):
        prompt = q.get("prompt")
        if not isinstance(prompt, str):
            continue
        new, reason = transform_prompt(prompt)
        if new is not None:
            q["prompt"] = new
            stats["restructured"] += 1
            samples.append((stats["file"], q["id"], new))
        elif reason == "short":
            stats["skipped_short"] += 1
        elif reason == "other":
            stats["skipped_other"] += 1
    out = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    if out != raw:
        path.write_text(out, encoding="utf-8")
    return stats


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=0, help="print N random restructured prompts")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    files = sorted((ROOT / "book" / "quiz").glob("grade-*.json")) + sorted(
        (ROOT / "book" / "quiz" / ".parts").glob("*.json")
    )
    samples: list = []
    tot_r = tot_s = tot_o = 0
    for f in files:
        s = process_file(f, samples)
        tot_r += s["restructured"]
        tot_s += s["skipped_short"]
        tot_o += s["skipped_other"]
        if s["restructured"] or s["skipped_short"] or s["skipped_other"]:
            print(
                f"{s['file']}: {s['restructured']} restructured, "
                f"{s['skipped_short']} skipped-short, {s['skipped_other']} skipped-other"
            )
    print(f"\nTOTAL: {tot_r} restructured, {tot_s} skipped-short, {tot_o} skipped-other")

    if args.samples and samples:
        rng = random.Random(args.seed)
        for f, qid, prompt in rng.sample(samples, min(args.samples, len(samples))):
            print(f"\n===== {f} :: {qid}")
            print(prompt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
