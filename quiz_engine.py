"""Adaptive, local-only quiz scheduling for the Farsi Java/Spring reader."""
from __future__ import annotations

import math
import random
from datetime import datetime, timedelta, timezone
from typing import Any


def now() -> datetime:
    return datetime.now(timezone.utc)


def stamp(value: datetime | None = None) -> str:
    return (value or now()).isoformat(timespec="seconds")


def parse_stamp(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value)
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def ensure_state(state: dict[str, Any]) -> dict[str, Any]:
    """Migrate the reader's old transparent state into adaptive state v2."""
    state["version"] = max(2, int(state.get("version", 1)))
    state.setdefault("chapters", {})
    state.setdefault("answers", {})
    state.setdefault("concepts", {})
    state.setdefault("sessions", {})
    for data in state["answers"].values():
        data.setdefault("attempts", 0)
        data.setdefault("correct", 0)
        data.setdefault("streak", 0)
        if "last_result" not in data and "last_correct" in data:
            data["last_result"] = bool(data["last_correct"])
        data.setdefault("next_due", None)
        data.setdefault("last_seen", None)
    for data in state["concepts"].values():
        data.setdefault("attempts", 0)
        data.setdefault("correct", 0)
        data.setdefault("streak", 0)
        data.setdefault("last_seen", None)
    return state


def mastery(stats: dict[str, Any] | None) -> float:
    """Smoothed 0..1 concept mastery; no attempts intentionally stays low."""
    if not stats:
        return 0.0
    attempts = int(stats.get("attempts", 0))
    correct = int(stats.get("correct", 0))
    # Beta(1, 1) prior avoids declaring one lucky answer "mastery".
    return (correct + 1) / (attempts + 2)


def learner_level(state: dict[str, Any]) -> float:
    concepts = list(state.get("concepts", {}).values())
    attempted = [item for item in concepts if int(item.get("attempts", 0))]
    if not attempted:
        return 1.0
    mean = sum(mastery(item) for item in attempted) / len(attempted)
    volume = sum(int(item.get("attempts", 0)) for item in attempted)
    # Growth is conservative: one correct response cannot jump to level five.
    return min(5.0, max(1.0, 1.0 + mean * 2.7 + min(0.9, volume / 180)))


def prerequisite_penalty(question: dict[str, Any], state: dict[str, Any]) -> float:
    prerequisites = question.get("prerequisites", [])
    if not prerequisites:
        return 1.0
    known = [mastery(state["concepts"].get(item)) for item in prerequisites]
    return 1.0 if not known else 0.35 + 0.65 * sum(known) / len(known)


def question_priority(question: dict[str, Any], state: dict[str, Any], review_only: bool = False) -> float:
    answer = state["answers"].get(question["id"])
    if not answer:
        base = 5.0
    else:
        base = 0.7
        if answer.get("last_result") is False:
            base += 8.0
        due = parse_stamp(answer.get("next_due"))
        if due is None or due <= now():
            base += 3.5
        else:
            seconds = max(1, (due - now()).total_seconds())
            base += min(1.5, 86_400 / seconds)

    concept_stats = [state["concepts"].get(c) for c in question.get("concepts", [])]
    weakness = 1 - (sum(mastery(s) for s in concept_stats) / len(concept_stats)) if concept_stats else 0.5
    base += weakness * 4.0

    if review_only and answer and answer.get("last_result") is not False:
        base *= 0.55
    elif review_only and not answer:
        base *= 0.25

    difficulty = int(question.get("difficulty", 1))
    target = learner_level(state)
    distance = abs(difficulty - target)
    base *= 1.35 if distance <= 0.65 else (0.85 if distance <= 1.5 else 0.45)
    return max(0.02, base * prerequisite_penalty(question, state))


def select_questions(
    questions: list[dict[str, Any]], state: dict[str, Any], count: int, review_only: bool = False
) -> list[dict[str, Any]]:
    """Weighted, without-replacement selection: novel + weak + due content."""
    state = ensure_state(state)
    pool = list(questions)
    selected: list[dict[str, Any]] = []

    # A lapse is never left to chance: the most recent missed questions lead a
    # review session. The remaining slots are still weighted-random, so review
    # does not become a predictable replay.
    if review_only:
        lapsed = sorted(
            (q for q in pool if state["answers"].get(q["id"], {}).get("last_result") is False),
            key=lambda q: state["answers"][q["id"]].get("last_seen") or "",
            reverse=True,
        )
        for question in lapsed[:max(1, count)]:
            selected.append(question)
            pool.remove(question)
            if len(selected) == count:
                return selected

    for _ in range(min(max(1, count) - len(selected), len(pool))):
        weights = [question_priority(q, state, review_only) for q in pool]
        picked = random.choices(pool, weights=weights, k=1)[0]
        selected.append(picked)
        pool.remove(picked)
    return selected


def normalize_text(value: object) -> str:
    return " ".join(str(value).strip().casefold().split())


def is_correct(question: dict[str, Any], response: str | set[str]) -> bool:
    expected = {normalize_text(item) for item in question.get("answers", [])}
    if isinstance(response, set):
        return {normalize_text(item) for item in response} == expected
    return normalize_text(response) in expected


def record_answer(question: dict[str, Any], correct: bool, state: dict[str, Any]) -> None:
    state = ensure_state(state)
    seen = stamp()
    answer = state["answers"].setdefault(question["id"], {})
    attempts = int(answer.get("attempts", 0)) + 1
    prior_streak = int(answer.get("streak", 0))
    streak = prior_streak + 1 if correct else 0
    answer.update({
        "attempts": attempts,
        "correct": int(answer.get("correct", 0)) + int(correct),
        "last_result": correct,
        "last_seen": seen,
        "streak": streak,
        # Wrong answers are immediately eligible. Correct intervals: 1, 3, 7, 14, 30 days.
        "next_due": stamp(now() + timedelta(days=(0 if not correct else min(30, [1, 3, 7, 14, 30][min(streak - 1, 4)])))),
    })
    for concept in question.get("concepts", []):
        stats = state["concepts"].setdefault(concept, {})
        stats.update({
            "attempts": int(stats.get("attempts", 0)) + 1,
            "correct": int(stats.get("correct", 0)) + int(correct),
            "streak": int(stats.get("streak", 0)) + 1 if correct else 0,
            "last_seen": seen,
        })


def mastery_rows(state: dict[str, Any]) -> list[tuple[str, float, int, int]]:
    rows = []
    for concept, stats in state.get("concepts", {}).items():
        rows.append((concept, mastery(stats), int(stats.get("correct", 0)), int(stats.get("attempts", 0))))
    return sorted(rows, key=lambda row: (row[1], -row[3], row[0]))
