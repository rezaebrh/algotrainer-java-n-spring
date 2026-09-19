"""Dependency-free bidi helpers for the Farsi terminal reader."""
from __future__ import annotations

import os
import re
import unicodedata

RLI = "⁧"
LRI = "⁦"
PDI = "⁩"

# Keep Markdown inline code and ordinary Latin/number phrases together as one
# left-to-right isolate inside a Persian line.
LTR_RUN = re.compile(
    r"`[^`]+`|"
    r"[A-Za-z0-9][A-Za-z0-9_./:+#?&=;@<>()\[\]{}'\"-]*"
    r"(?:\s+[A-Za-z0-9][A-Za-z0-9_./:+#?&=;@<>()\[\]{}'\"-]*)*"
)


def base_direction(text: str) -> str:
    """Treat a line containing Persian/Arabic letters as RTL."""
    return "R" if any(unicodedata.bidirectional(char) in {"R", "AL"} for char in text) else "L"


def isolate_ltr_runs(text: str) -> str:
    """Protect inline English identifiers, numbers, and Markdown code."""
    return LTR_RUN.sub(lambda match: f"{LRI}{match.group(0)}{PDI}", text)


def visual_order(text: str) -> str:
    """Add Unicode isolates; a bidi-capable terminal performs visual ordering."""
    if base_direction(text) != "R" or os.environ.get("JAVABOOK_BIDI") == "off":
        return text
    return f"{RLI}{isolate_ltr_runs(text)}{PDI}"


def right_align(text: str, width: int) -> str:
    """Pad by display characters, ignoring zero-width bidi controls."""
    controls = {RLI, LRI, PDI}
    visible_width = sum(char not in controls for char in text)
    return " " * max(0, width - visible_width) + text


def align_rtl(lines: list[str], width: int, starts_in_code_fence: bool = False) -> list[str]:
    """Right-align Persian prose while leaving fenced and indented code alone."""
    aligned: list[str] = []
    in_code_fence = starts_in_code_fence
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("```"):
            in_code_fence = not in_code_fence
            aligned.append(line)
        elif not stripped or line.startswith("    ") or in_code_fence:
            aligned.append(line)
        elif base_direction(stripped) == "R":
            aligned.append(right_align(visual_order(stripped), width))
        else:
            aligned.append(line)
    return aligned
