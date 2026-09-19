#!/usr/bin/env python3
"""Normalize, merge, and validate local question banks for the CLI book."""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
QUIZ = ROOT / "book" / "quiz"
PARTS = QUIZ / ".parts"
VALID_TYPES = {"mcq", "multi", "tf", "blank"}
DIFFICULTIES = {"easy": 1, "medium": 3, "hard": 4, "advanced": 5}


def normalize_answers(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if value is None:
        return []
    return [str(value)]


def normalize_question(question: dict[str, Any]) -> dict[str, Any]:
    item = dict(question)
    item["type"] = str(item.get("type", "mcq")).casefold()
    item["answers"] = normalize_answers(item.get("answers", item.get("answer")))
    difficulty = item.get("difficulty", 1)
    if isinstance(difficulty, str):
        difficulty = DIFFICULTIES.get(difficulty.casefold(), 3)
    item["difficulty"] = int(difficulty)
    item["concepts"] = [str(value) for value in item.get("concepts", [])]
    item["prerequisites"] = [str(value) for value in item.get("prerequisites", [])]

    options = item.get("options")
    if item["type"] in {"mcq", "multi"}:
        if isinstance(options, list):
            item["options"] = {chr(ord("A") + index): str(value) for index, value in enumerate(options)}
        elif isinstance(options, dict):
            item["options"] = {str(key).upper(): str(value) for key, value in options.items()}
        else:
            item["options"] = {}
    else:
        item.pop("options", None)
    return item


def validate_question(question: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    identity = question.get("id", "<missing id>")
    for field in ("id", "type", "prompt", "answers", "explanation", "concepts", "difficulty", "prerequisites"):
        if field not in question:
            errors.append(f"{identity}: missing {field}")
    if question.get("type") not in VALID_TYPES:
        errors.append(f"{identity}: invalid type {question.get('type')!r}")
    if not isinstance(question.get("prompt"), str) or not question.get("prompt", "").strip():
        errors.append(f"{identity}: prompt must be non-empty text")
    if not question.get("answers"):
        errors.append(f"{identity}: no answers")
    difficulty = question.get("difficulty")
    if not isinstance(difficulty, int) or not 1 <= difficulty <= 5:
        errors.append(f"{identity}: difficulty must be 1..5")
    if not question.get("concepts"):
        errors.append(f"{identity}: at least one concept is required")
    if question.get("type") in {"mcq", "multi"}:
        options = question.get("options", {})
        if not isinstance(options, dict) or not 2 <= len(options) <= 4:
            errors.append(f"{identity}: mcq/multi must have 2..4 options")
        else:
            missing = set(question.get("answers", [])) - set(options)
            if missing:
                errors.append(f"{identity}: answer(s) not in options: {sorted(missing)}")
            if question.get("type") == "mcq" and len(question.get("answers", [])) != 1:
                errors.append(f"{identity}: mcq must have exactly one answer")
            if question.get("type") == "multi" and len(question.get("answers", [])) < 2:
                errors.append(f"{identity}: multi must have at least two answers")
    if question.get("type") == "tf":
        normalized = {answer.casefold() for answer in question.get("answers", [])}
        if normalized not in ({"true"}, {"false"}, {"درست"}, {"نادرست"}):
            errors.append(f"{identity}: tf answer must be true/false")
    return errors


def read_questions(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [normalize_question(question) for question in data.get("questions", [])]


def merge_grade_one() -> None:
    all_questions: list[dict[str, Any]] = []
    for path in sorted(PARTS.glob("g1-*.json")):
        all_questions.extend(read_questions(path))
    # Parts are disjoint by ID; deterministic sort makes diffs and sessions reproducible.
    all_questions.sort(key=lambda question: question["id"])
    output = {
        "title": "درجهٔ ۱ — آجرهای سازندهٔ Java 21",
        "version": 2,
        "questions": all_questions,
    }
    (QUIZ / "grade-01.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def merge_grade_two() -> None:
    """Append authored Grade 2 parts to the checked-in seed bank deterministically."""
    target = QUIZ / "grade-02.json"
    seeds = [
        question for question in read_questions(target)
        if question.get("id", "").startswith("g2-seed-")
    ]
    additions: list[dict[str, Any]] = []
    for path in sorted(PARTS.glob("g2-*.json")):
        additions.extend(read_questions(path))
    questions = seeds + additions
    questions.sort(key=lambda question: question["id"])
    target.write_text(
        json.dumps(
            {
                "title": "درجهٔ ۲ — عملگرها و جریان کنترل",
                "version": 2,
                "questions": questions,
            },
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )


def merge_seed_banks() -> None:
    grouped: dict[int, list[dict[str, Any]]] = {grade: [] for grade in range(3, 13)}
    for path in sorted(PARTS.glob("grades-*-seeds.json")):
        for question in read_questions(path):
            grade = int(question["id"].split("-", 1)[0][1:])
            if grade in grouped:
                grouped[grade].append(question)
    for grade, questions in grouped.items():
        if not questions:
            continue
        questions.sort(key=lambda question: question["id"])
        (QUIZ / f"grade-{grade:02d}.json").write_text(
            json.dumps({"title": f"درجهٔ {grade}", "version": 2, "questions": questions}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )


def validate_all() -> int:
    failures: list[str] = []
    duplicate_ids: list[str] = []
    ids: set[str] = set()
    counts: dict[str, int] = {}
    concepts: Counter[str] = Counter()
    difficulties: Counter[int] = Counter()
    types: Counter[str] = Counter()
    prompts: dict[str, list[str]] = defaultdict(list)
    for path in sorted(QUIZ.glob("grade-*.json")):
        questions = read_questions(path)
        counts[path.stem] = len(questions)
        for question in questions:
            if question.get("id") in ids:
                duplicate_id = str(question.get("id"))
                duplicate_ids.append(duplicate_id)
                failures.append(f"duplicate id: {duplicate_id}")
            ids.add(question.get("id", ""))
            failures.extend(validate_question(question))
            concepts.update(question.get("concepts", []))
            difficulties.update([question.get("difficulty", 0)])
            types.update([question.get("type", "<missing>")])
            normalized_prompt = " ".join(str(question.get("prompt", "")).casefold().split())
            if normalized_prompt:
                prompts[normalized_prompt].append(str(question.get("id", "<missing id>")))
    if counts.get("grade-01", 0) < 400:
        failures.append(f"grade-01 needs >=400 questions; has {counts.get('grade-01', 0)}")
    for grade in range(2, 13):
        if counts.get(f"grade-{grade:02d}", 0) < 15:
            failures.append(f"grade-{grade:02d} needs >=15 questions")
    duplicate_prompts = [ids for ids in prompts.values() if len(ids) > 1]
    print("Question counts:", ", ".join(f"{name}={count}" for name, count in counts.items()))
    print("Type distribution:", dict(sorted(types.items())))
    print(f"Duplicate IDs: {'none' if not duplicate_ids else duplicate_ids}")
    print(f"Duplicate normalized prompts: {'none' if not duplicate_prompts else duplicate_prompts}")
    print(f"Schema errors: {len(failures)}")
    print("Corpus concepts:", ", ".join(f"{name}={count}" for name, count in sorted(concepts.items()) if name))
    print("Difficulty distribution:", dict(sorted(difficulties.items())))
    if failures:
        print("VALIDATION FAILED:", *failures, sep="\n- ", file=sys.stderr)
        return 1
    print(f"VALID: {sum(counts.values())} questions, {len(ids)} unique IDs")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--merge", action="store_true", help="normalize .parts and rebuild final banks")
    args = parser.parse_args()
    if args.merge:
        merge_grade_one()
        merge_grade_two()
        merge_seed_banks()
    return validate_all()


if __name__ == "__main__":
    raise SystemExit(main())
