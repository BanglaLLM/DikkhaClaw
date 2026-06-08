"""QuestionLookup tool — search the question bank by subject, topic, year, difficulty."""

from __future__ import annotations

import json
import os
from typing import Any

from clawpy.tool.base import Permission, RunContext, ToolResult


class QuestionLookupTool:
    """Search the question bank for practice questions."""

    _questions: list[dict[str, Any]] | None = None

    @property
    def name(self) -> str:
        return "QuestionLookup"

    @property
    def description(self) -> str:
        return (
            "Search the question bank for practice questions. "
            "Filter by subject, topic, year, difficulty, or exam type (DU/BUET/Medical)."
        )

    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "subject": {
                    "type": "string",
                    "description": "Subject: physics, chemistry, math, biology, english, bangla, gk",
                },
                "topic": {
                    "type": "string",
                    "description": "Specific topic within the subject (e.g. 'organic chemistry', 'calculus')",
                },
                "difficulty": {
                    "type": "string",
                    "enum": ["easy", "medium", "hard"],
                    "description": "Difficulty level",
                },
                "exam_type": {
                    "type": "string",
                    "description": "Target exam: DU, BUET, Medical, or general",
                },
                "year": {
                    "type": "integer",
                    "description": "Year of the question (e.g. 2023)",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max number of questions to return (default 5)",
                },
            },
            "required": [],
        }

    def permission_for(self, input: dict[str, Any]) -> Permission:
        return Permission.READ_ONLY

    def is_read_only(self, input: dict[str, Any]) -> bool:
        return True

    def _load_questions(self) -> list[dict[str, Any]]:
        if self._questions is not None:
            return self._questions

        bank_path = os.environ.get(
            "DIKKHA_QUESTION_BANK",
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "data", "question_bank.json"),
        )
        try:
            with open(bank_path, encoding="utf-8") as f:
                self._questions = json.load(f)
        except FileNotFoundError:
            self._questions = []
        return self._questions

    async def run(self, input: dict[str, Any], ctx: RunContext) -> ToolResult:
        questions = self._load_questions()
        if not questions:
            return ToolResult(content="Question bank is empty. No questions loaded.", is_error=True)

        results = questions
        subject = input.get("subject", "").lower()
        if subject:
            results = [q for q in results if q.get("subject", "").lower() == subject]

        topic = input.get("topic", "").lower()
        if topic:
            results = [
                q for q in results
                if topic in q.get("topic", "").lower()
                or topic in " ".join(q.get("tags", [])).lower()
            ]

        difficulty = input.get("difficulty", "").lower()
        if difficulty:
            results = [q for q in results if q.get("difficulty", "").lower() == difficulty]

        exam_type = input.get("exam_type", "").lower()
        if exam_type:
            results = [
                q for q in results
                if exam_type in q.get("exam_type", "").lower()
                or exam_type in " ".join(q.get("tags", [])).lower()
            ]

        year = input.get("year")
        if year:
            results = [q for q in results if q.get("year") == year]

        limit = input.get("limit", 5)
        results = results[:limit]

        if not results:
            return ToolResult(content="No questions found matching the criteria.")

        output = json.dumps(results, ensure_ascii=False, indent=2)
        return ToolResult(content=f"Found {len(results)} question(s):\n{output}")
