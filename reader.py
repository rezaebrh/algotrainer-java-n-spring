#!/usr/bin/env python3
"""خوانندهٔ محلی و تطبیقی کتاب Java/Spring؛ بدون وابستگی خارجی."""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import textwrap
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from quiz_engine import ensure_state, is_correct, learner_level, mastery_rows, record_answer, select_questions
from rtl import align_rtl

ROOT = Path(__file__).resolve().parent
DEFAULT_BOOK_DIR = ROOT / "book"


def default_state_path() -> Path:
    base = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state"))
    return base / "java-spring-farsi-book" / "progress.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def empty_state() -> dict[str, Any]:
    return ensure_state({"version": 2, "chapters": {}, "answers": {}, "concepts": {}, "sessions": {}})


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return empty_state()
    try:
        return ensure_state(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError) as error:
        print(f"Cannot read progress state: {error}", file=sys.stderr)
        return empty_state()


def save_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def find_chapters(book_dir: Path) -> list[Path]:
    return sorted(path for path in book_dir.glob("*.md") if path.is_file())


def chapter_title(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem


def choose_chapter(chapters: list[Path], selector: str | None) -> Path:
    if not chapters:
        raise FileNotFoundError("No Markdown chapter was found.")
    if selector is None:
        return chapters[0]
    if selector.isdigit() and 1 <= int(selector) <= len(chapters):
        return chapters[int(selector) - 1]
    matches = [path for path in chapters if selector.casefold() in path.stem.casefold()]
    if len(matches) == 1:
        return matches[0]
    raise ValueError(f"Unknown chapter: {selector}")


def wrap_markdown(source: str, width: int) -> list[str]:
    width = max(36, width)
    output: list[str] = []
    paragraph: list[str] = []
    in_code_fence = False

    def flush() -> None:
        nonlocal paragraph
        if paragraph:
            text = " ".join(item.strip() for item in paragraph)
            output.extend(textwrap.wrap(text, width=width, break_long_words=False, break_on_hyphens=False) or [""])
            paragraph = []

    for raw in source.splitlines():
        stripped = raw.strip()
        if stripped.startswith("```"):
            flush(); in_code_fence = not in_code_fence; output.append(raw)
        elif in_code_fence or raw.startswith("    "):
            flush(); output.append(raw)
        elif not stripped:
            flush(); output.append("")
        elif raw.startswith("#"):
            flush(); output.append(raw)
        elif raw.startswith(("- ", "* ", "> ")) or re.match(r"^\d+\. ", raw):
            flush()
            output.extend(textwrap.wrap(raw, width=width, subsequent_indent="  ", break_long_words=False) or [raw])
        else:
            paragraph.append(raw)
    flush()
    return output


def paginate(lines: list[str], terminal_rows: int) -> list[list[str]]:
    rows_per_page = max(5, terminal_rows - 4)
    return [lines[index:index + rows_per_page] for index in range(0, len(lines), rows_per_page)] or [[]]


def clear_screen() -> None:
    print("\033[2J\033[H", end="")


def show_page(chapter: Path, pages: list[list[str]], page: int) -> None:
    columns = min(shutil.get_terminal_size((80, 24)).columns, 100)
    clear_screen()
    print(f"{chapter_title(chapter)} | صفحه {page + 1} از {len(pages)}")
    print("─" * columns)
    starts_in_code_fence = sum(
        line.lstrip().startswith("```") for earlier_page in pages[:page] for line in earlier_page
    ) % 2 == 1
    print("\n".join(align_rtl(pages[page], columns, starts_in_code_fence)))
    print("─" * columns)
    print("Enter/n: بعد | p: قبل | g N: صفحه | c: فصل‌ها | s: وضعیت | q: خروج")


def show_chapters(chapters: list[Path], state: dict[str, Any]) -> None:
    print("فصل‌ها:")
    for index, chapter in enumerate(chapters, start=1):
        saved = state["chapters"].get(chapter.name)
        if not saved:
            progress = "شروع نشده"
        else:
            total = max(1, int(saved.get("total_pages", 1)))
            progress = f"آخرین صفحه: {min(total, int(saved.get('page', 0)) + 1)}/{total}"
        print(f"  {index}. {chapter_title(chapter)} [{progress}]")


def show_status(chapters: list[Path], state: dict[str, Any]) -> None:
    print("وضعیت خواندن:")
    for chapter in chapters:
        saved = state["chapters"].get(chapter.name)
        if not saved:
            print(f"  {chapter_title(chapter)}: هنوز شروع نشده")
            continue
        total = max(1, int(saved.get("total_pages", 1)))
        current = min(total, int(saved.get("page", 0)) + 1)
        print(f"  {chapter_title(chapter)}: صفحهٔ {current}/{total} ({current / total:.0%})")

    attempts = sum(int(item.get("attempts", 0)) for item in state["answers"].values())
    correct = sum(int(item.get("correct", 0)) for item in state["answers"].values())
    print(f"\nآزمون: {attempts} پاسخ، {correct} درست، دقت {correct / attempts:.0%}" if attempts else "\nآزمون: هنوز پاسخی ثبت نشده است.")
    print(f"سطح تخمینی فعلی: {learner_level(state):.1f}/5")
    rows = mastery_rows(state)
    if rows:
        print("\nمهارت‌ها (کمترین mastery در بالا):")
        for concept, score, hit, seen in rows[:12]:
            bar = "█" * round(score * 12) + "░" * (12 - round(score * 12))
            print(f"  {concept:26} {bar} {score:.0%} ({hit}/{seen})")


def read_chapter(chapter: Path, chapters: list[Path], state: dict[str, Any], state_file: Path) -> None:
    size = shutil.get_terminal_size((80, 24))
    lines = wrap_markdown(chapter.read_text(encoding="utf-8"), size.columns - 2)
    pages = paginate(lines, size.lines)
    saved = state["chapters"].get(chapter.name, {})
    page = min(max(0, int(saved.get("page", 0))), len(pages) - 1)
    while True:
        show_page(chapter, pages, page)
        command = input("> ").strip(); lowered = command.casefold()
        if lowered in {"q", "quit", "خروج"}: break
        if lowered in {"", "n", "next", "بعد"}: page = min(page + 1, len(pages) - 1)
        elif lowered in {"p", "prev", "قبل"}: page = max(0, page - 1)
        elif lowered.startswith("g "):
            try: page = min(max(0, int(command.split(maxsplit=1)[1]) - 1), len(pages) - 1)
            except ValueError: input("شمارهٔ صفحه نامعتبر است. Enter را بزنید.")
        elif lowered in {"c", "chapters", "فصل"}:
            clear_screen(); show_chapters(chapters, state); input("برای بازگشت Enter را بزنید.")
        elif lowered in {"s", "status", "وضعیت"}:
            clear_screen(); show_status(chapters, state); input("برای بازگشت Enter را بزنید.")
        else: input("فرمان ناشناخته است. Enter را بزنید.")
        state["chapters"][chapter.name] = {"page": page, "total_pages": len(pages), "updated_at": utc_now()}
        save_state(state_file, state)
    state["chapters"][chapter.name] = {"page": page, "total_pages": len(pages), "updated_at": utc_now()}
    save_state(state_file, state)


def load_questions(quiz_directory: Path, quiz_name: str | None = None) -> list[dict[str, Any]]:
    paths = [quiz_directory / f"{quiz_name}.json"] if quiz_name else sorted(quiz_directory.glob("grade-*.json"))
    questions: list[dict[str, Any]] = []
    for path in paths:
        if not path.exists(): raise FileNotFoundError(f"Quiz bank not found: {path}")
        questions.extend(json.loads(path.read_text(encoding="utf-8")).get("questions", []))
    return questions


def response_for(question: dict[str, Any]) -> str | set[str]:
    kind = question["type"]
    if kind in {"mcq", "multi"}:
        for key, text in question["options"].items(): print(f"  {key}. {text}")
        valid = {key.upper() for key in question["options"]}
        if kind == "mcq":
            while True:
                response = input("پاسخ: ").strip().upper()
                if response in valid: return response
                print("یکی از گزینه‌های نمایش‌داده‌شده را وارد کنید.")
        while True:
            raw = input("پاسخ‌ها (مثلاً A,C): ").upper().replace(" ", "")
            response = {part for part in raw.split(",") if part}
            if response and response <= valid: return response
            print("برای چندانتخابی، حروف گزینه‌ها را با ویرگول جدا کنید.")
    if kind == "tf":
        while True:
            raw = input("پاسخ (true/false یا درست/نادرست): ").strip().casefold()
            if raw in {"true", "false", "درست", "نادرست"}: return raw
            print("true یا false وارد کنید.")
    return input("پاسخ کوتاه: ").strip()


def ask(questions: list[dict[str, Any]], state: dict[str, Any], state_file: Path) -> None:
    for position, question in enumerate(questions, start=1):
        print(f"\nپرسش {position}/{len(questions)} | {question['id']} | سطح {question.get('difficulty', 1)} | {question['type']}")
        print(question["prompt"])
        if question.get("hint"):
            print(f"راهنما: {question['hint']}")
        response = response_for(question)
        correct = is_correct(question, response)
        answer_text = ", ".join(question["answers"])
        print("✓ درست است." if correct else f"✗ نادرست است؛ پاسخ درست: {answer_text}.")
        print(question["explanation"])
        record_answer(question, correct, state)
        save_state(state_file, state)


def main() -> int:
    parser = argparse.ArgumentParser(description="خوانندهٔ محلی و تطبیقی کتاب Java/Spring")
    parser.add_argument("--book-dir", type=Path, default=DEFAULT_BOOK_DIR)
    parser.add_argument("--state", type=Path, default=default_state_path())
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="فهرست فصل‌ها")
    reading = commands.add_parser("read", help="خواندن تعاملی یک فصل"); reading.add_argument("chapter", nargs="?")
    commands.add_parser("status", help="نمایش پیشرفت و mastery")
    quiz = commands.add_parser("quiz", help="جلسهٔ تطبیقی از یک بانک پرسش")
    quiz.add_argument("name", help="نام JSON بدون پسوند، مانند grade-01"); quiz.add_argument("--count", type=int, default=10)
    review = commands.add_parser("review", help="مرور تطبیقیِ خطاها و مفاهیم ضعیف")
    review.add_argument("--count", type=int, default=10)
    args = parser.parse_args(); state = load_state(args.state); chapters = find_chapters(args.book_dir)
    try:
        if args.command == "list": show_chapters(chapters, state)
        elif args.command == "read": read_chapter(choose_chapter(chapters, args.chapter), chapters, state, args.state)
        elif args.command == "status": show_status(chapters, state)
        elif args.command == "quiz": ask(select_questions(load_questions(args.book_dir / "quiz", args.name), state, args.count), state, args.state)
        elif args.command == "review": ask(select_questions(load_questions(args.book_dir / "quiz"), state, args.count, review_only=True), state, args.state)
    except (FileNotFoundError, ValueError, json.JSONDecodeError, KeyError) as error:
        print(f"Error: {error}", file=sys.stderr); return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
