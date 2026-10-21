#!/usr/bin/env python3
"""Audit where inline code still mixes with Persian text in the quiz banks."""
import json, re, glob

SPAN = re.compile(r"`([^`\n]+)`")
FENCE = "```"
STRONG = (";", "=", "(", ")", "{", "}", "[", "]", ":", "...", "->", "<<", ">>", ">>>", "&&", "||", "++", "--", "=>")
OP = re.compile(r"[+\-*/%<>!&|^]")

def is_code(s):
    return any(t in s for t in STRONG) or (OP.search(s) and " " in s)

tot_prompt = tot_opt = tot_expl = 0
for fn in sorted(glob.glob("book/quiz/grade-*.json")):
    d = json.load(open(fn))
    for q in d["questions"]:
        p = q.get("prompt", "")
        if FENCE not in p and any(is_code(s) for s in SPAN.findall(p)):
            tot_prompt += 1
        for o in (q.get("options") or {}).values():
            if any(is_code(s) for s in SPAN.findall(str(o))):
                tot_opt += 1
                break
        e = q.get("explanation", "")
        if any(is_code(s) for s in SPAN.findall(e)):
            tot_expl += 1

print("prompts with inline code remaining:", tot_prompt)
print("questions with code in options:", tot_opt)
print("explanations with inline code:", tot_expl)
