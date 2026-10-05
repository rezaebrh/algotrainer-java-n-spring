#!/usr/bin/env python3
"""خوانندهٔ محلی و تطبیقی کتاب Java/Spring؛ بدون وابستگی خارجی."""
from __future__ import annotations

import argparse
import json
import os
import random
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

# Terminal-vs-log behaviour, flipped on in main(). The interactive path is the
# default product and must stay byte-for-byte unchanged when a TTY is attached.
NON_INTERACTIVE = False
RENDER_WIDTH = 100
# A log has no height, so non-interactive page size is a fixed constant.
NON_TTY_ROWS = 40


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
    if NON_INTERACTIVE:
        return
    print("\033[2J\033[H", end="")


def show_page(chapter: Path, pages: list[list[str]], page: int, columns: int) -> None:
    clear_screen()
    print(f"{chapter_title(chapter)} | صفحه {page + 1} از {len(pages)}")
    print("─" * columns)
    starts_in_code_fence = sum(
        line.lstrip().startswith("```") for earlier_page in pages[:page] for line in earlier_page
    ) % 2 == 1
    print("\n".join(align_rtl(pages[page], columns, starts_in_code_fence)))
    print("─" * columns)
    if not NON_INTERACTIVE:
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


def parse_pages(spec: str | None, total: int) -> list[int]:
    """Turn a `--pages` spec ("3", "2-5", unset) into 0-based page indices."""
    if spec is None or not spec.strip() or spec.strip().casefold() == "all":
        return list(range(total))
    match = re.fullmatch(r"\s*(\d+)\s*(?:-\s*(\d+)\s*)?", spec)
    if not match:
        raise ValueError(f"Invalid --pages value: {spec}")
    first = int(match.group(1))
    last = int(match.group(2) or first)
    if first < 1 or last < first:
        raise ValueError(f"Invalid --pages range: {spec}")
    return [number - 1 for number in range(first, min(last, total) + 1)]


def render_chapter(chapter: Path, width: int, pages_spec: str | None) -> None:
    """Print a chapter's pages to a log without prompting or saving progress."""
    lines = wrap_markdown(chapter.read_text(encoding="utf-8"), width - 2)
    pages = paginate(lines, NON_TTY_ROWS)
    for page in parse_pages(pages_spec, len(pages)):
        show_page(chapter, pages, page, width)


def read_chapter(chapter: Path, chapters: list[Path], state: dict[str, Any], state_file: Path,
                 pages_spec: str | None = None) -> None:
    if NON_INTERACTIVE:
        render_chapter(chapter, RENDER_WIDTH, pages_spec)
        return
    size = shutil.get_terminal_size((80, 24))
    columns = min(size.columns, 100)
    lines = wrap_markdown(chapter.read_text(encoding="utf-8"), size.columns - 2)
    pages = paginate(lines, size.lines)
    saved = state["chapters"].get(chapter.name, {})
    page = min(max(0, int(saved.get("page", 0))), len(pages) - 1)
    while True:
        show_page(chapter, pages, page, columns)
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


def terminal_columns(cap: int = 100, fallback: int = 80) -> int:
    """Best-effort terminal width; never returns zero or an absurdly small value."""
    try:
        columns = shutil.get_terminal_size((fallback, 24)).columns
    except (OSError, ValueError):
        return fallback
    if columns < 20:
        return fallback
    return min(columns, cap)


def format_rtl_block(text: str, width: int) -> str:
    """Apply align_rtl to a possibly multi-line string for terminal output.

    Reuses the same bidi treatment the `read` path uses: right-align Persian
    prose and protect embedded English/code/number runs with Unicode isolates.
    Honors JAVABOOK_BIDI=off via rtl.visual_order internally.
    """
    lines = text.splitlines() or [""]
    return "\n".join(align_rtl(lines, width, starts_in_code_fence=False))


def load_questions(quiz_directory: Path, quiz_name: str | None = None) -> list[dict[str, Any]]:
    paths = [quiz_directory / f"{quiz_name}.json"] if quiz_name else sorted(quiz_directory.glob("grade-*.json"))
    questions: list[dict[str, Any]] = []
    for path in paths:
        if not path.exists(): raise FileNotFoundError(f"Quiz bank not found: {path}")
        questions.extend(json.loads(path.read_text(encoding="utf-8")).get("questions", []))
    return questions


def print_options(question: dict[str, Any], width: int) -> None:
    if question["type"] not in {"mcq", "multi"}:
        return
    for key, text in question["options"].items():
        print(format_rtl_block(f"  {key}. {text}", width))


def parse_answer(question: dict[str, Any], raw: str) -> str | set[str]:
    """Normalize a raw answer line into the shape `is_correct` expects."""
    kind = question["type"]
    if kind == "multi":
        return {part for part in raw.upper().replace(" ", "").split(",") if part}
    if kind == "mcq":
        return raw.strip().upper()
    if kind == "tf":
        return raw.strip().casefold()
    return raw.strip()


def response_for(question: dict[str, Any], width: int, source: str | None = None) -> str | set[str]:
    print_options(question, width)
    if source is not None:
        # A supplied answer bypasses the retry loops: an invalid one is graded
        # wrong instead of prompting again, which would exhaust the source.
        return parse_answer(question, source)
    kind = question["type"]
    if kind in {"mcq", "multi"}:
        valid = {key.upper() for key in question["options"]}
        if kind == "mcq":
            while True:
                response = parse_answer(question, input(format_rtl_block("پاسخ: ", width)))
                if response in valid:
                    return response
                print(format_rtl_block("یکی از گزینه‌های نمایش‌داده‌شده را وارد کنید.", width))
        while True:
            response = parse_answer(question, input(format_rtl_block("پاسخ‌ها (مثلاً A,C): ", width)))
            if response and response <= valid:
                return response
            print(format_rtl_block("برای چندانتخابی، حروف گزینه‌ها را با ویرگول جدا کنید.", width))
    if kind == "tf":
        while True:
            response = parse_answer(question, input(format_rtl_block("پاسخ (true/false یا درست/نادرست): ", width)))
            if response in {"true", "false", "درست", "نادرست"}:
                return response
            print(format_rtl_block("true یا false وارد کنید.", width))
    return input(format_rtl_block("پاسخ کوتاه: ", width)).strip()


def load_answers(inline: str | None, path: Path | None) -> list[str] | None:
    """Parse supplied answers; `--answers-file` (one per line) wins over `--answers`."""
    if path is not None:
        text = sys.stdin.read() if str(path) == "-" else path.read_text(encoding="utf-8")
        return [line.strip() for line in text.splitlines() if line.strip()]
    if inline is None:
        return None
    # Semicolons separate questions, so a comma can stay inside a multi answer.
    return [part.strip() for part in inline.split(";")]


def show_questions(questions: list[dict[str, Any]], width: int) -> None:
    """Print the selected questions without grading — the `--show` preview."""
    for position, question in enumerate(questions, start=1):
        print(format_rtl_block(f"پرسش {position}/{len(questions)} | {question['id']} | سطح {question.get('difficulty', 1)} | {question['type']}", width))
        print(format_rtl_block(question["prompt"], width))
        if question.get("hint"):
            print(format_rtl_block(f"راهنما: {question['hint']}", width))
        print_options(question, width)


def ask(questions: list[dict[str, Any]], state: dict[str, Any], state_file: Path,
        width: int | None = None, answers: list[str] | None = None) -> None:
    columns = width if width is not None else terminal_columns()
    source = iter(answers) if answers is not None else None
    for position, question in enumerate(questions, start=1):
        print(format_rtl_block(f"پرسش {position}/{len(questions)} | {question['id']} | سطح {question.get('difficulty', 1)} | {question['type']}", columns))
        print(format_rtl_block(question["prompt"], columns))
        if question.get("hint"):
            print(format_rtl_block(f"راهنما: {question['hint']}", columns))
        if source is None:
            response = response_for(question, columns)
        else:
            try:
                supplied = next(source)
            except StopIteration:
                print(format_rtl_block("پاسخ‌های ورودی تمام شد؛ جلسه در همین‌جا پایان یافت.", columns))
                break
            response = response_for(question, columns, supplied)
        correct = is_correct(question, response)
        answer_text = ", ".join(question["answers"])
        verdict = "✓ درست است." if correct else f"✗ نادرست است؛ پاسخ درست: {answer_text}."
        print(format_rtl_block(verdict, columns))
        print(format_rtl_block(question["explanation"], columns))
        record_answer(question, correct, state)
        save_state(state_file, state)


def add_answer_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--answers", help="پاسخ‌های ازپیش‌داده‌شده؛ میان پرسش‌ها با «;» جدا می‌شوند")
    parser.add_argument("--answers-file", type=Path, help="پروندهٔ پاسخ‌ها، هر خط یک پاسخ؛ - یعنی stdin")
    parser.add_argument("--seed", type=int, help="seed برای انتخاب تکرارپذیر پرسش‌ها")
    parser.add_argument("--show", action="store_true", help="فقط نمایش پرسش‌های انتخابی، بدون نمره‌دهی")


def main() -> int:
    global NON_INTERACTIVE, RENDER_WIDTH
    parser = argparse.ArgumentParser(description="خوانندهٔ محلی و تطبیقی کتاب Java/Spring")
    parser.add_argument("--book-dir", type=Path, default=DEFAULT_BOOK_DIR)
    parser.add_argument("--state", type=Path, default=default_state_path())
    parser.add_argument("--no-tty", action="store_true", help="حالت غیرتعاملی برای اجرا در CI و لاگ")
    parser.add_argument("--width", type=int, help="عرض رندر در حالت غیرتعاملی")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="فهرست فصل‌ها")
    reading = commands.add_parser("read", help="خواندن تعاملی یک فصل")
    reading.add_argument("chapter", nargs="?")
    reading.add_argument("--pages", help="در حالت غیرتعاملی: یک صفحه یا بازه، مانند ۳ یا ۲-۵")
    commands.add_parser("status", help="نمایش پیشرفت و mastery")
    quiz = commands.add_parser("quiz", help="جلسهٔ تطبیقی از یک بانک پرسش")
    quiz.add_argument("name", help="نام JSON بدون پسوند، مانند grade-01"); quiz.add_argument("--count", type=int, default=10)
    add_answer_options(quiz)
    review = commands.add_parser("review", help="مرور تطبیقیِ خطاها و مفاهیم ضعیف")
    review.add_argument("--count", type=int, default=10)
    add_answer_options(review)
    args = parser.parse_args(); state = load_state(args.state); chapters = find_chapters(args.book_dir)
    NON_INTERACTIVE = args.no_tty or not sys.stdin.isatty()
    RENDER_WIDTH = args.width or (100 if NON_INTERACTIVE else terminal_columns())
    columns = RENDER_WIDTH
    if getattr(args, "seed", None) is not None: random.seed(args.seed)
    try:
        if args.command == "list": show_chapters(chapters, state)
        elif args.command == "read": read_chapter(choose_chapter(chapters, args.chapter), chapters, state, args.state, args.pages)
        elif args.command == "status": show_status(chapters, state)
        elif args.command == "quiz":
            questions = select_questions(load_questions(args.book_dir / "quiz", args.name), state, args.count)
            if args.show: show_questions(questions, columns)
            else: ask(questions, state, args.state, columns, load_answers(args.answers, args.answers_file))
        elif args.command == "review":
            questions = select_questions(load_questions(args.book_dir / "quiz"), state, args.count, review_only=True)
            if args.show: show_questions(questions, columns)
            else: ask(questions, state, args.state, columns, load_answers(args.answers, args.answers_file))
    except EOFError:
        print("Error: no interactive input available; use --no-tty for non-interactive runs.", file=sys.stderr); return 2
    except (FileNotFoundError, ValueError, json.JSONDecodeError, KeyError) as error:
        print(f"Error: {error}", file=sys.stderr); return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
