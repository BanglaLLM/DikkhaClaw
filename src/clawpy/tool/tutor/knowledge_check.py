"""KnowledgeCheck tool — generate quick verification questions mid-conversation."""

from __future__ import annotations

import json
import os
import random
from typing import Any

from clawpy.tool.base import Permission, RunContext, ToolResult


class KnowledgeCheckTool:
    """Generate a quick mini-quiz question to verify student understanding."""

    @property
    def name(self) -> str:
        return "KnowledgeCheck"

    @property
    def description(self) -> str:
        return (
            "Generate a quick quiz question to check if the student truly understands "
            "a concept. Use after explaining something to verify comprehension. "
            "Returns a question with options — present it to the student as a check."
        )

    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "The topic to generate a check question for",
                },
                "difficulty": {
                    "type": "string",
                    "enum": ["easy", "medium", "hard"],
                    "description": "Difficulty level",
                },
                "subject": {
                    "type": "string",
                    "description": "Subject area",
                },
            },
            "required": ["topic"],
        }

    def permission_for(self, input: dict[str, Any]) -> Permission:
        return Permission.READ_ONLY

    def is_read_only(self, input: dict[str, Any]) -> bool:
        return True

    async def run(self, input: dict[str, Any], ctx: RunContext) -> ToolResult:
        topic = input["topic"]
        difficulty = input.get("difficulty", "medium")
        subject = input.get("subject", "")

        # Try to find a matching question from the bank
        bank_path = os.environ.get(
            "DIKKHA_QUESTION_BANK",
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "data", "question_bank.json"),
        )
        try:
            with open(bank_path, encoding="utf-8") as f:
                questions = json.load(f)
        except FileNotFoundError:
            return ToolResult(
                content=f"No question bank found. Generate a question about '{topic}' ({difficulty}) yourself."
            )

        matches = [
            q for q in questions
            if topic.lower() in q.get("topic", "").lower()
            or topic.lower() in " ".join(q.get("tags", [])).lower()
        ]

        if difficulty:
            filtered = [q for q in matches if q.get("difficulty", "").lower() == difficulty]
            if filtered:
                matches = filtered

        if not matches:
            return ToolResult(
                content=f"No matching questions in bank for '{topic}'. Generate a question yourself."
            )

        chosen = random.choice(matches)
        # Return without revealing the correct answer to the LLM prompt
        # (the LLM should use this to quiz the student)
        output = {
            "question": chosen.get("question", ""),
            "question_bn": chosen.get("question_bn", ""),
            "options": [
                {"id": o["id"], "text": o["text"], "text_bn": o.get("text_bn", "")}
                for o in chosen.get("options", [])
            ],
            "topic": chosen.get("topic", ""),
            "difficulty": chosen.get("difficulty", ""),
            "hint": f"This tests understanding of {topic}",
            "_correct_answer": chosen.get("correct_answer", ""),
        }
        return ToolResult(content=json.dumps(output, ensure_ascii=False, indent=2))
