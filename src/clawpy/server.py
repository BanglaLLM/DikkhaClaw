"""DikkhaClaw — Koji-style Bangla AI tutor backend.

Run:
    python -m clawpy.server
    # or
    uvicorn clawpy.server:app --port 4039

Built on the ClawPy engine. Creates a tutor Engine per student session,
uses Socratic dialogue to teach, and streams responses as SSE.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import uuid
from typing import Any

from clawpy.config.config import Config
from clawpy.engine.engine import Engine
from clawpy.provider.base import EventType, StreamEvent
from clawpy.tool.permission import PermissionEnforcer, PermissionMode
from clawpy.tool.registry import ToolRegistry

logger = logging.getLogger("clawpy.server")

# Concurrency limiter — subscription rate limits are tight
_query_semaphore = asyncio.Semaphore(2)

# ── Engine factory ─────────────────────────────────────────────────────────

_engines: dict[str, Engine] = {}


def _create_provider(config: Config):
    """Create the LLM provider from config."""
    import clawpy.provider.anthropic  # noqa: F401
    import clawpy.provider.openai  # noqa: F401
    import clawpy.provider.gemini  # noqa: F401
    import clawpy.provider.ollama  # noqa: F401
    import clawpy.provider.deepseek  # noqa: F401

    from clawpy.provider.registry import create

    provider_cfg = config.provider_config()
    return create(config.provider, provider_cfg)


def _build_tools(engine: Engine) -> ToolRegistry:
    """Register tutor tools for Dikkha."""
    from clawpy.tool.web_fetch import WebFetchTool
    from clawpy.tool.tutor.question_lookup import QuestionLookupTool
    from clawpy.tool.tutor.student_profile import StudentProfileTool
    from clawpy.tool.tutor.knowledge_check import KnowledgeCheckTool

    registry = ToolRegistry()
    registry.register(QuestionLookupTool())
    registry.register(StudentProfileTool())
    registry.register(KnowledgeCheckTool())
    registry.register(WebFetchTool())
    return registry


async def _connect_mcp_servers(registry: ToolRegistry, config: Config) -> list:
    """Discover and connect MCP servers, adding their tools to the registry."""
    from clawpy.mcp.client import MCPClient, MCPToolWrapper, load_mcp_configs

    mcp_configs = load_mcp_configs(config.work_dir)
    clients = []

    for server_cfg in mcp_configs:
        try:
            client = MCPClient(server_cfg)
            await client.connect()
            for spec in client.tool_specs():
                registry.register(MCPToolWrapper(client, spec))
            clients.append(client)
            logger.info("Connected MCP server '%s' with %d tools", server_cfg.name, len(client.tools))
        except Exception as e:
            logger.warning("Failed to connect MCP server '%s': %s", server_cfg.name, e)

    return clients


def _get_server_config() -> Config:
    """Build config for server mode."""
    cfg = Config()
    cfg.work_dir = os.environ.get("CLAWPY_WORK_DIR", os.getcwd())
    cfg.provider = os.environ.get("CLAWPY_PROVIDER", "anthropic")
    cfg.model = os.environ.get("CLAWPY_MODEL", "claude-sonnet-4-6")
    cfg.max_tokens = int(os.environ.get("CLAWPY_MAX_TOKENS", "16384"))
    cfg.permission_mode = "bypass"
    return cfg


async def get_or_create_engine(session_id: str | None = None) -> tuple[str, Engine]:
    """Get an existing engine or create a new one for a session."""
    from clawpy.session.session import SessionStore

    sid = session_id or str(uuid.uuid4())

    if sid in _engines:
        return sid, _engines[sid]

    config = _get_server_config()
    provider = _create_provider(config)
    enforcer = PermissionEnforcer(
        mode=PermissionMode.BYPASS,
        work_dir=config.work_dir,
    )

    engine = Engine(
        provider=provider,
        tools=ToolRegistry(),
        enforcer=enforcer,
        config=config,
    )
    engine.tools = _build_tools(engine)

    await _connect_mcp_servers(engine.tools, config)

    from clawpy.prompts.dikkha import build_dikkha_prompt
    engine.set_system_prompt(build_dikkha_prompt())

    store = SessionStore(sid)
    previous = store.load_session()
    if previous:
        engine.messages = previous
        logger.info("Resumed session '%s' with %d messages", sid, len(previous))
    else:
        store.save_meta(config.model, config.work_dir)
    engine.session_store = store

    _engines[sid] = engine
    return sid, engine


# ── SSE formatting ─────────────────────────────────────────────────────────

def _format_sse(event: str, data: dict) -> str:
    """Format a single SSE event line."""
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def stream_event_to_sse(
    event: StreamEvent,
    tools_called: list[str],
) -> str | None:
    """Convert a ClawPy StreamEvent to an SSE-formatted string."""
    match event.type:
        case EventType.DELTA:
            if event.delta and event.delta.text:
                return _format_sse("token", {"text": event.delta.text})
        case EventType.TOOL_START:
            if event.tool_call:
                tools_called.append(event.tool_call.name)
                return _format_sse("tool_use", {
                    "name": event.tool_call.name,
                    "input": event.tool_call.input if hasattr(event.tool_call, 'input') else {},
                })
        case EventType.TOOL_END:
            if event.tool_call:
                return _format_sse("tool_result", {
                    "name": event.tool_call.name,
                    "summary": f"Completed {event.tool_call.name}",
                })
        case EventType.ERROR:
            msg = event.delta.text if event.delta else "Unknown error"
            return _format_sse("error", {"message": msg})
    return None


# ── FastAPI app ────────────────────────────────────────────────────────────

try:
    from fastapi import FastAPI, Request
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import StreamingResponse
    from pydantic import BaseModel
except ImportError:
    raise ImportError("FastAPI is required for server mode: pip install fastapi uvicorn")


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    system_prompt: str | None = None
    context_type: str | None = None
    context_id: str | None = None
    context_data: dict | None = None


class SuggestionsResponse(BaseModel):
    suggestions: list[str]


app = FastAPI(
    title="DikkhaClaw",
    description="দীক্ষা — Koji-style Bangla AI Tutor for ShikkhaDikkha",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/tutor/stream")
async def tutor_stream(req: ChatRequest):
    """Stream a tutor response as SSE events — main chat endpoint."""
    session_id, engine = await get_or_create_engine(req.session_id)

    if req.system_prompt:
        engine.set_system_prompt(req.system_prompt)
    elif req.context_type:
        from clawpy.prompts.dikkha import build_dikkha_prompt
        ctx = req.context_data or {}
        if req.context_id:
            ctx["context_id"] = req.context_id
        engine.set_system_prompt(build_dikkha_prompt(
            context_type=req.context_type,
            context_data=ctx or None,
        ))

    tools_called: list[str] = []
    collected_events: list[StreamEvent] = []

    def on_stream(event: StreamEvent) -> None:
        collected_events.append(event)

    async def generate():
        yield _format_sse("progress", {"step": "starting", "session_id": session_id})

        task = asyncio.create_task(
            engine.run_turn(req.message, on_stream=on_stream)
        )

        while not task.done():
            while collected_events:
                ev = collected_events.pop(0)
                sse = stream_event_to_sse(ev, tools_called)
                if sse:
                    yield sse
            await asyncio.sleep(0.05)

        while collected_events:
            ev = collected_events.pop(0)
            sse = stream_event_to_sse(ev, tools_called)
            if sse:
                yield sse

        result = task.result()
        yield _format_sse("done", {
            "session_id": session_id,
            "model": engine.config.model,
            "tools_called": tools_called,
            "stop_reason": result.stop_reason.value if result.stop_reason else "end_turn",
            "usage": {
                "input_tokens": result.usage.input_tokens,
                "output_tokens": result.usage.output_tokens,
            },
        })

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.get("/tutor/suggestions", response_model=SuggestionsResponse)
async def get_suggestions(context_type: str = "free_chat", subject: str | None = None):
    """Return context-aware starter prompts for the chat UI."""
    if context_type == "exam_question":
        return SuggestionsResponse(suggestions=[
            "এই প্রশ্নটা কিভাবে সমাধান করবো?",
            "Can you give me a hint?",
            "এখানে কোন concept কাজে লাগবে?",
            "Why is my answer wrong?",
        ])
    elif context_type == "exam_review":
        return SuggestionsResponse(suggestions=[
            "আমার সবচেয়ে দুর্বল বিষয় কোনটা?",
            "Explain my mistakes one by one",
            "এই ভুলগুলো থেকে কি pattern দেখা যাচ্ছে?",
            "Give me practice questions on my weak areas",
        ])
    elif subject:
        subject_prompts = {
            "physics": ["Newton's laws বুঝিয়ে বলো", "Solve a circuit problem with me"],
            "chemistry": ["Organic naming practice করি", "Acid-base কনসেপ্ট clear করো"],
            "math": ["Integration practice করি", "Logarithm এর basic থেকে শুরু করো"],
            "biology": ["Cell biology revision করি", "Photosynthesis explain করো"],
        }
        return SuggestionsResponse(suggestions=subject_prompts.get(subject, [
            "আজ কোন বিষয় পড়বে?",
            "তোমার দুর্বল বিষয় নিয়ে কাজ করি?",
            "একটা mock test দিতে চাও?",
            "গতকালের ভুলগুলো review করি?",
        ]))
    return SuggestionsResponse(suggestions=[
        "আজ কোন বিষয় পড়বে?",
        "Physics practice শুরু করি?",
        "BUET এর গত বছরের প্রশ্ন দেখাও",
        "আমার weak areas কী কী?",
        "একটা quick quiz দাও!",
        "Calculus এর chain rule বুঝিয়ে দাও",
    ])


class HintRequest(BaseModel):
    question_id: str
    student_answer: str | None = None
    session_id: str | None = None
    user_id: str | None = None


class ExplainRequest(BaseModel):
    question_id: str
    student_answer: str | None = None
    correct_answer: str | None = None
    session_id: str | None = None


@app.post("/tutor/hint")
async def tutor_hint(req: HintRequest):
    """Quick Socratic hint for a specific question — non-streaming, fast."""
    import json as _json
    # Load the question
    bank_path = os.environ.get(
        "DIKKHA_QUESTION_BANK",
        os.path.join(os.path.dirname(__file__), "..", "..", "data", "question_bank.json"),
    )
    try:
        with open(bank_path, encoding="utf-8") as f:
            questions = _json.load(f)
    except FileNotFoundError:
        return {"hint": "Question bank not found.", "error": True}

    question = next((q for q in questions if q["id"] == req.question_id), None)
    if not question:
        return {"hint": "Question not found.", "error": True}

    # Build a focused prompt for a quick hint
    session_id, engine = await get_or_create_engine(req.session_id)
    from clawpy.prompts.dikkha import build_dikkha_prompt
    engine.set_system_prompt(build_dikkha_prompt(
        context_type="exam_question",
        context_data=question,
    ))

    hint_prompt = f"I'm stuck on this question."
    if req.student_answer:
        hint_prompt += f" I think the answer is {req.student_answer}. Am I right?"
    hint_prompt += " Give me a hint without telling me the answer."

    result = await engine.run_turn(hint_prompt)

    # Extract text from result
    text = ""
    for msg in result.messages:
        if msg.role.value == "assistant":
            for block in msg.content:
                if hasattr(block, 'text') and block.text:
                    text = block.text
                    break

    return {
        "hint": text,
        "session_id": session_id,
        "question_id": req.question_id,
    }


@app.post("/tutor/explain")
async def tutor_explain(req: ExplainRequest):
    """Full step-by-step explanation after exam — non-streaming."""
    import json as _json
    bank_path = os.environ.get(
        "DIKKHA_QUESTION_BANK",
        os.path.join(os.path.dirname(__file__), "..", "..", "data", "question_bank.json"),
    )
    try:
        with open(bank_path, encoding="utf-8") as f:
            questions = _json.load(f)
    except FileNotFoundError:
        return {"explanation": "Question bank not found.", "error": True}

    question = next((q for q in questions if q["id"] == req.question_id), None)
    if not question:
        return {"explanation": "Question not found.", "error": True}

    session_id, engine = await get_or_create_engine(req.session_id)
    from clawpy.prompts.dikkha import build_dikkha_prompt
    engine.set_system_prompt(build_dikkha_prompt(
        context_type="exam_review",
        context_data={"mistakes": [question]},
    ))

    prompt = f"I got this question wrong."
    if req.student_answer:
        prompt += f" I chose {req.student_answer}."
    if req.correct_answer:
        prompt += f" The correct answer is {req.correct_answer}."
    prompt += " Please explain step by step why the correct answer is right and where I went wrong."

    result = await engine.run_turn(prompt)

    text = ""
    for msg in result.messages:
        if msg.role.value == "assistant":
            for block in msg.content:
                if hasattr(block, 'text') and block.text:
                    text = block.text
                    break

    return {
        "explanation": text,
        "session_id": session_id,
        "question_id": req.question_id,
    }


MODEL_MAX_OUTPUT_TOKENS = {
    "claude-opus-4-8": 128000,
    "claude-opus-4-7": 128000,
    "claude-opus-4-6": 128000,
    "claude-sonnet-4-6": 64000,
    "claude-sonnet-4-5-20250929": 64000,
    "claude-haiku-4-5-20251001": 64000,
}


def _resolve_max_tokens(model: str | None, requested: int | None) -> int:
    """Use the model's actual max if no explicit limit requested."""
    if requested and requested > 0:
        return requested
    if model and model in MODEL_MAX_OUTPUT_TOKENS:
        return MODEL_MAX_OUTPUT_TOKENS[model]
    for key, val in MODEL_MAX_OUTPUT_TOKENS.items():
        if model and key.startswith(model):
            return val
    return 64000


class QueryRequest(BaseModel):
    """Simple non-streaming LLM query — no agentic loop, no tools."""
    prompt: str
    system_prompt: str | None = None
    model: str | None = None
    provider: str | None = None
    max_tokens: int | None = None
    temperature: float | None = None
    fallback_models: list[str] | None = None


@app.post("/tutor/query")
async def simple_query(req: QueryRequest):
    """Direct LLM call — fast, no tools, no agentic loop.

    Use for batch pipeline tasks: content extraction, summarization,
    selector generation, classification, etc.

    Supports provider/model override and automatic fallback chain.
    """
    models_to_try = []
    if req.model:
        models_to_try.append((req.provider, req.model))
    else:
        models_to_try.append((None, None))

    if req.fallback_models:
        for fm in req.fallback_models:
            if ":" in fm:
                p, m = fm.split(":", 1)
                models_to_try.append((p, m))
            else:
                models_to_try.append((None, fm))

    async with _query_semaphore:
        return await _execute_query(req, models_to_try)


async def _execute_query(req: QueryRequest, models_to_try: list):
    import time as _time
    from clawpy.provider.base import Request as ProviderRequest
    from clawpy.types import ContentType, Role, text_message

    last_error = None
    for provider_name, model_name in models_to_try:
        cfg = _get_server_config()
        if provider_name:
            cfg.provider = provider_name
        if model_name:
            cfg.model = model_name

        provider = _create_provider(cfg)
        target_model = model_name or cfg.model

        messages = [text_message(Role.USER, req.prompt)]

        resolved_max = _resolve_max_tokens(target_model, req.max_tokens)

        provider_req = ProviderRequest(
            model=target_model,
            system=req.system_prompt or "",
            messages=messages,
            tools=[],
            max_tokens=resolved_max,
            temperature=req.temperature,
        )

        # Retry with exponential backoff for rate limits (429)
        max_retries = 5
        for attempt in range(max_retries):
            try:
                start = _time.time()
                response = await provider.send(provider_req)
                elapsed = _time.time() - start

                content = ""
                for block in response.content:
                    if block.type == ContentType.TEXT:
                        content += block.text

                return {
                    "success": True,
                    "content": content,
                    "model": target_model,
                    "provider": provider_name or cfg.provider,
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "execution_time": round(elapsed, 2),
                }
            except Exception as e:
                last_error = str(e)
                if "429" in str(e) and attempt < max_retries - 1:
                    wait = 2 ** attempt * 10  # 10s, 20s, 40s, 80s, 160s
                    logger.info(f"Rate limited, retrying in {wait}s (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(wait)
                    continue
                prov = provider_name or "default"
                mod = model_name or "default"
                logger.warning(f"Query failed ({prov}/{mod}): {last_error}")
                break

    return {"success": False, "error": last_error or "All models failed", "content": ""}


@app.get("/tutor/health")
async def health():
    return {"status": "ok", "engines": len(_engines)}


@app.get("/tutor/accounts")
async def account_status():
    """Show account pool status — which accounts are available, rate-limited, etc."""
    try:
        from clawpy.auth.account_pool import get_pool
        pool = get_pool()
        return pool.get_status()
    except Exception as e:
        return {"error": str(e), "total_accounts": 0}


# ── Curriculum API ────────────────────────────────────────────────────────

class LessonPlanRequest(BaseModel):
    student_id: str
    target_exam: str = "general"  # du, buet, medical, gst, general
    difficulty: str = "medium"  # easy, medium, hard
    subjects: list[str] | None = None
    weak_topics: list[str] | None = None
    max_lessons: int | None = None


@app.get("/curriculum/subjects")
async def list_subjects():
    """List all available subjects with their unit/lesson counts."""
    from clawpy.curriculum.planner import get_subject_overview
    from clawpy.curriculum.models import SubjectId

    results = []
    for sid in SubjectId:
        overview = get_subject_overview(sid)
        if "error" not in overview:
            results.append({
                "id": overview["subject"],
                "title": overview["title"],
                "title_bn": overview["title_bn"],
                "icon": overview["icon"],
                "target_exams": overview["target_exams"],
                "total_units": overview["total_units"],
                "total_lessons": overview["total_lessons"],
            })
    return {"subjects": results}


@app.get("/curriculum/subjects/{subject_id}")
async def get_subject(subject_id: str):
    """Get full curriculum tree for a subject — units and lessons."""
    from clawpy.curriculum.planner import get_subject_overview
    from clawpy.curriculum.models import SubjectId

    try:
        sid = SubjectId(subject_id)
    except ValueError:
        return {"error": f"Unknown subject: {subject_id}"}
    return get_subject_overview(sid)


@app.get("/curriculum/lessons/{lesson_id}")
async def get_lesson(lesson_id: str):
    """Get details of a specific lesson."""
    from clawpy.curriculum.planner import get_lesson_detail
    result = get_lesson_detail(lesson_id)
    if not result:
        return {"error": f"Lesson not found: {lesson_id}"}
    return result


@app.post("/curriculum/plan")
async def create_lesson_plan(req: LessonPlanRequest):
    """Generate a personalized Duolingo-style lesson plan."""
    from clawpy.curriculum.planner import generate_lesson_plan
    from clawpy.curriculum.models import Difficulty, SubjectId, TargetExam

    try:
        target = TargetExam(req.target_exam)
    except ValueError:
        target = TargetExam.GENERAL

    try:
        diff = Difficulty(req.difficulty)
    except ValueError:
        diff = Difficulty.MEDIUM

    subjects = None
    if req.subjects:
        subjects = []
        for s in req.subjects:
            try:
                subjects.append(SubjectId(s))
            except ValueError:
                pass

    plan = generate_lesson_plan(
        student_id=req.student_id,
        target_exam=target,
        difficulty=diff,
        subjects=subjects or None,
        weak_topics=req.weak_topics,
        max_lessons=req.max_lessons,
    )

    return {
        "id": plan.id,
        "title": plan.title,
        "title_bn": plan.title_bn,
        "target_exam": plan.target_exam.value,
        "difficulty": plan.difficulty.value,
        "subjects": [s.value for s in plan.subjects],
        "total_lessons": plan.total_lessons,
        "estimated_hours": plan.estimated_hours,
        "path": plan.path,
    }


@app.get("/curriculum/exams")
async def list_exams():
    """List available target exams and their subjects."""
    from clawpy.curriculum.syllabus import EXAM_SUBJECTS
    return {
        "exams": {
            exam.value: {
                "subjects": [s.value for s in subjects],
                "label": _exam_label(exam.value),
                "label_bn": _exam_label_bn(exam.value),
            }
            for exam, subjects in EXAM_SUBJECTS.items()
        }
    }


def _exam_label(exam: str) -> str:
    return {
        "du": "Dhaka University", "buet": "BUET (Engineering)",
        "medical": "Medical Admission", "ru": "Rajshahi University",
        "ju": "Jahangirnagar University", "cu": "Chittagong University",
        "gst": "GST (Combined)", "general": "General Preparation",
    }.get(exam, exam.upper())


def _exam_label_bn(exam: str) -> str:
    return {
        "du": "ঢাকা বিশ্ববিদ্যালয়", "buet": "বুয়েট (ইঞ্জিনিয়ারিং)",
        "medical": "মেডিকেল ভর্তি", "ru": "রাজশাহী বিশ্ববিদ্যালয়",
        "ju": "জাহাঙ্গীরনগর বিশ্ববিদ্যালয়", "cu": "চট্টগ্রাম বিশ্ববিদ্যালয়",
        "gst": "জিএসটি (সম্মিলিত)", "general": "সাধারণ প্রস্তুতি",
    }.get(exam, exam.upper())


def main():
    """Run the server with uvicorn."""
    import uvicorn

    port = int(os.environ.get("CLAWPY_SERVER_PORT", "4039"))
    host = os.environ.get("CLAWPY_SERVER_HOST", "0.0.0.0")
    logger.info("Starting DikkhaClaw tutor on %s:%d", host, port)
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
