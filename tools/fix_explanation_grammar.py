#!/usr/bin/env python3
"""Fix the broken grammar produced by the in-place explanation fence insertions.

The restructure_explanations.py pass inserted «کد زیر را در نظر بگیرید» at the
code's original position, which breaks sentences when the code was a mid-sentence
object («برای X ... است» → dangling preposition, split verbs). This script
replaces each affected explanation with a hand-written correct version. Matching
is by a ZWNJ-free prefix key; replacements build ZWNJ via chr(0x200c).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
Z = chr(0x200c)

FIXES = [
    # (ZWNJ-free prefix key, full replacement)
    ("Math.random بازهٔ کد زیر",
     "Math.random مقداری در بازهٔ زیر تولید می" + Z + "کند:\n\n```java\n[0.0, 1.0)\n```\n\n"
     "عدد 1.0 در این بازه نیست؛ تنها 0.0 ممکن است تولید شود."),

    ("floorDiv و floorMod تقسیم",
     "floorDiv و floorMod تقسیم و باقیمانده را به" + Z + "گونه" + Z + "ای تعریف می" + Z + "کنند که همواره "
     "رابطهٔ زیر برقرار باشد، حتی برای ورودی منفی:\n\n```java\na == (a / b) * b + (a % b)\n```"),

    ("sin آرگومان را بر حسب رادیان",
     "sin آرگومان را بر حسب رادیان می" + Z + "گیرد نه درجه؛ برای تبدیل درجه به رادیان باید در عدد زیر "
     "ضرب کرد:\n\n```java\nMath.PI / 180\n```"),

    ("atan2 زاویهٔ بردار",
     "atan2 زاویهٔ بردار (x, y) را نسبت به محور x مثبت بر حسب رادیان در بازهٔ زیر برمی" + Z + "گرداند و "
     "برای تقسیم" + Z + "بندی چهارربع صفحه مناسب است:\n\n```java\n(-π, π]\n```"),

    ("برای کد زیر را در نظر بگیرید:\n\n```java\nrecord User",
     "کد زیر را در نظر بگیرید:\n\n```java\nrecord User(String name)\n```\n\naccessor همان name() است."),

    ("syntax label برابر کد زیر",
     "syntax label برابر شکل زیر است:\n\n```java\nname: statement\n```"),

    ("early return در void فقط با کد زیر",
     "در متد void، خروج زودهنگام فقط با دستور زیر و بدون expression مجاز است:\n\n```java\nreturn;\n```"),

    ("شکل کوتاه initializer تنها در اعلام متغیر مجاز است؛ برای تخصیص بعدی باید از کد زیر",
     "شکل کوتاه initializer تنها در اعلام متغیر مجاز است؛ برای تخصیص بعدی باید از کد زیر استفاده کرد:\n\n"
     "```java\nnew int[]{...}\n```"),

    ("`length` فیلد final عمومی آرایه",
     "`length` فیلد final عمومی آرایه است و بدون پرانتز خوانده می" + Z + "شود؛ در حالی که متدهای نمونهٔ "
     "String و List با پرانتز فراخوانی می" + Z + "شوند:\n\n```java\nString.length()\nList.size()\n```"),

    ("شرط `<=` به جای `<`",
     "شرط `<=` به جای `<` یک اندیس بیش از حد می" + Z + "دهد و در تکرار آخر:\n\n```java\na[a.length]\n```\n\n"
     "خطای out of bounds رخ می" + Z + "دهد."),
]

files = sorted((ROOT / "book" / "quiz").glob("grade-*.json")) + sorted((ROOT / "book" / "quiz" / ".parts").glob("*.json"))
total = 0
for f in files:
    raw = f.read_text(encoding="utf-8")
    data = json.loads(raw)
    changed = 0
    for q in data.get("questions", []):
        e = q.get("explanation", "")
        for key, new in FIXES:
            if e.startswith(key):
                if e != new:
                    q["explanation"] = new
                    changed += 1
                break
    if changed:
        f.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"{f.relative_to(ROOT)}: {changed} fixed")
        total += changed
print(f"TOTAL: {total}")
