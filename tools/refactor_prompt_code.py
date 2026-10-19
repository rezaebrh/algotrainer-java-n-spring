#!/usr/bin/env python3
"""Move code snippets embedded in quiz prompts into separate fenced blocks.

Prompt shape before:  «خروجی `int x = 5;` چیست؟»  (LTR code inside RTL prose)
Prompt shape after:   کد زیر را در نظر بگیرید:
                      ```java
                      int x = 5;
                      ```
                      خروجی کد بالا چیست؟

A backtick span is "extractable code" when it carries real code punctuation
( ; = ( ) { } [ ] : ... -> << >> >>> && || ++ -- ) or an operator together
with a space. Single identifiers (`switch`, `equals`, `Math.floorMod`) stay
inline. Only prompts with exactly one extractable span are restructured;
multi-span and already-multi-line prompts are counted and skipped so a human
can review them. The same deterministic transform runs on published banks and
on .parts sources so future merges reproduce identical output.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPAN = re.compile(r"`([^`\n]+)`")

STRONG = (";", "=", "(", ")", "{", "}", "[", "]", ":", "...", "->", "<<", ">>", ">>>", "&&", "||", "++", "--", "=>")
OPERATOR = re.compile(r"[+\-*/%<>!&|^]")


def is_code(span: str) -> bool:
    if any(tok in span for tok in STRONG):
        return True
    if OPERATOR.search(span) and " " in span:
        return True
    return False


LEAD_IN = "کد زیر را در نظر بگیرید:"
REFERENCE = "کد بالا"


def transform_prompt(prompt: str):
    """Return the restructured prompt, or None when not applicable."""
    if "\n" in prompt:
        return None  # already multi-line; leave for review
    spans = SPAN.findall(prompt)
    extractable = [s for s in spans if is_code(s)]
    if len(extractable) != 1:
        return None
    code = extractable[0]
    # Replace only the extractable span (first occurrence of its exact text).
    idx = prompt.find("`" + code + "`")
    if idx < 0:
        return None
    sentence = prompt[:idx] + REFERENCE + prompt[idx + len(code) + 2:]
    sentence = re.sub(r"\s+", " ", sentence).strip()
    return f"{LEAD_IN}\n\n```java\n{code}\n```\n\n{sentence}"


def process_file(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    questions = data.get("questions", [])
    stats = {"file": str(path.relative_to(ROOT)), "total": len(questions), "changed": 0, "multi": 0, "multiline": 0}
    for q in questions:
        prompt = q.get("prompt")
        if not isinstance(prompt, str) or "`" not in prompt:
            continue
        new = transform_prompt(prompt)
        if new is None:
            if "\n" in prompt:
                stats["multiline"] += 1
            elif sum(1 for s in SPAN.findall(prompt) if is_code(s)) > 1:
                stats["multi"] += 1
            continue
        q["prompt"] = new
        stats["changed"] += 1
    out = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    if out != raw:
        path.write_text(out, encoding="utf-8")
    return stats


files = sorted((ROOT / "book" / "quiz").glob("grade-*.json")) + sorted((ROOT / "book" / "quiz" / ".parts").glob("*.json"))
tot_changed = tot_multi = tot_multiline = 0
for f in files:
    s = process_file(f)
    tot_changed += s["changed"]
    tot_multi += s["multi"]
    tot_multiline += s["multiline"]
    if s["changed"] or s["multi"] or s["multiline"]:
        print(f"{s['file']}: {s['changed']}/{s['total']} restructured, {s['multi']} multi-span, {s['multiline']} multiline")
print(f"\nTOTAL: {tot_changed} restructured, {tot_multi} multi-span skipped, {tot_multiline} multiline skipped")
