"""JSON-in / JSON-out wrappers so the browser can drive quiz_engine.py unchanged.

No browser concerns live here, so this module runs identically under CPython
(for tests) and under Pyodide. Everything crosses the boundary as JSON strings,
which sidesteps Pyodide's JS<->Python proxy conversion entirely, and the state
is the same JSON shape reader.py writes to progress.json — so progress can be
moved between the CLI and the web app.

See web/app.js for the calling side.
"""
from __future__ import annotations

import json

from quiz_engine import (
    ensure_state,
    is_correct,
    learner_level,
    mastery_rows,
    record_answer,
    select_questions,
)


def select(questions_json: str, state_json: str, count: int, review_only: bool = False) -> str:
    """Pick a session; returns {"questions": [...], "state": {...}}."""
    state = ensure_state(json.loads(state_json))
    questions = json.loads(questions_json)
    picked = select_questions(questions, state, int(count), bool(review_only))
    return json.dumps({"questions": picked, "state": state}, ensure_ascii=False)


def grade(question_json: str, response_json: str, state_json: str) -> str:
    """Grade one answer; returns {"correct": bool, "state": {...}}.

    A JSON list response means a multi-select question; is_correct() expects a
    set for those and a plain string for everything else.
    """
    question = json.loads(question_json)
    state = ensure_state(json.loads(state_json))
    response = json.loads(response_json)
    if isinstance(response, list):
        response = {str(part) for part in response}
    correct = is_correct(question, response)
    record_answer(question, correct, state)
    return json.dumps({"correct": correct, "state": state}, ensure_ascii=False)


def summary(state_json: str) -> str:
    """Return {"level": float, "mastery": [[concept, score, correct, attempts], ...]}."""
    state = ensure_state(json.loads(state_json))
    rows = [[concept, score, hit, seen] for concept, score, hit, seen in mastery_rows(state)]
    return json.dumps({"level": learner_level(state), "mastery": rows}, ensure_ascii=False)
