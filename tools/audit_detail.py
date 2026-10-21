#!/usr/bin/env python3
"""Detailed audit of remaining inline code in the published quiz banks.

Companion to tools/audit_inline_code.py — same "code" predicate, more detail:
  - IDs of questions whose prompt still has inline extractable code
  - histogram of qualifying spans per such prompt
  - pure-code options vs Persian+code mixed options
  - verbatim dump of 10 multi-span prompts
"""
import json, re, glob

SPAN = re.compile(r"`([^`\n]+)`")
PURE = re.compile(r"^\s*`([^`\n]+)`\s*$")
FENCE = "```"
STRONG = (";", "=", "(", ")", "{", "}", "[", "]", ":", "...", "->", "<<", ">>", ">>>", "&&", "||", "++", "--", "=>")
OP = re.compile(r"[+\-*/%<>!&|^]")
LETTER_PREFIX = re.compile(r"^[A-Da-d]\s*[).:\-]\s+")

def is_code(s: str) -> bool:
    return any(t in s for t in STRONG) or (OP.search(s) and " " in s)

def strip_letter_prefix(text: str) -> str:
    return LETTER_PREFIX.sub("", text, count=1)

def spans(text: str):
    return [m.group(1) for m in SPAN.finditer(text)]

def outside_spans(text: str) -> str:
    return SPAN.sub(" ", text)

flagged = []  # (id, [qualifying spans], prompt)
pure_any = pure_qual = 0        # whole option text is a single `...` span
mixed_qual = 0                  # prose + at least one qualifying code span
span_only_qual = 0              # 2+ spans, no prose between (all-code text)

for fn in sorted(glob.glob("book/quiz/grade-*.json")):
    d = json.load(open(fn, encoding="utf-8"))
    for q in d.get("questions", []):
        p = str(q.get("prompt", ""))
        if FENCE not in p:
            qual = [s for s in spans(p) if is_code(s)]
            if qual:
                flagged.append((q.get("id", "<missing id>"), qual, p))
        opts = q.get("options")
        if isinstance(opts, dict):
            opt_texts = [str(v) for v in opts.values()]
        elif isinstance(opts, list):
            opt_texts = [str(v) for v in opts]
        else:
            opt_texts = []
        for raw in opt_texts:
            body = strip_letter_prefix(raw)
            qual = [s for s in spans(body) if is_code(s)]
            m = PURE.match(body)
            if m:
                pure_any += 1
                if is_code(m.group(1)):
                    pure_qual += 1
            elif qual and outside_spans(body).strip():
                mixed_qual += 1
            elif qual:
                span_only_qual += 1

ids = [i for i, _, _ in flagged]
print("== Prompts with inline extractable code ==")
print("first 15 IDs:", ids[:15])
print("total count:", len(ids))

hist = {"1": 0, "2": 0, "3": 0, "4+": 0}
for _, qual, _ in flagged:
    n = len(qual)
    hist["1" if n == 1 else "2" if n == 2 else "3" if n == 3 else "4+"] += 1
print("== Histogram: qualifying spans per prompt ==")
for k in ("1", "2", "3", "4+"):
    print(f"  {k} span(s): {hist[k]}")

print("== Options ==")
print("pure-code options (entire text is a single backtick span):", pure_any,
      "(of which qualifying per code predicate:", pure_qual, ")")
print("mixed options (prose + inline code):", mixed_qual)
print("span-only options (2+ spans, no prose):", span_only_qual)

print("== Sample of 10 multi-span prompts (2+ qualifying spans) ==")
multi = [(i, p) for i, qual, p in flagged if len(qual) >= 2]
for i, p in multi[:10]:
    print(f"--- {i} ---")
    print(p)
print("(multi-span prompts total:", len(multi), ")")
