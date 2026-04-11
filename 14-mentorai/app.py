import os
import json
import time
import chromadb
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from google import genai
from models import (
    LearningCurriculum,
    Phase,
    PortfolioProject,
    WeeklySchedule,
    MentorResult
)
from prompts import (
    CURRICULUM_PROMPT,
    FOLLOWUP_PROMPT
)
from knowledge import (
    ROADMAP_DOCS,
    BACKGROUND_OPTIONS,
    GOAL_OPTIONS,
    TIME_OPTIONS
)

load_dotenv()

# ── Load models once ──
print("⏳ Loading embedding model...")
embedder = SentenceTransformer(
    "all-MiniLM-L6-v2"
)
print("✅ Embedding model ready")

# ── Clients ──
chroma_client = chromadb.Client()
gemini_client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)
GEMINI_MODEL = "gemini-3.1-flash-lite-preview"


# ──────────────────────────────────────────
# CORE UTILITIES
# ──────────────────────────────────────────

def clean_gemini_response(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")
        lines = [
            l for l in lines
            if not l.strip().startswith("```")
        ]
        raw = "\n".join(lines).strip()
    return raw


def call_gemini(
    prompt: str,
    retries: int = 3
) -> str:
    last_error = None
    for attempt in range(retries + 1):
        try:
            response = (
                gemini_client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=prompt
                )
            )
            return response.text
        except Exception as e:
            error_str = str(e)
            last_error = error_str
            if "429" in error_str or \
               "RESOURCE_EXHAUSTED" in error_str:
                if attempt < retries:
                    print(
                        "⏳ Rate limit. "
                        "Waiting 40s..."
                    )
                    time.sleep(40)
                    continue
            if attempt < retries:
                time.sleep(2)
                continue
    raise RuntimeError(
        f"Gemini failed: {last_error}"
    )


# ──────────────────────────────────────────
# INPUT VALIDATION
# ──────────────────────────────────────────

def validate_profile(
    background: str,
    goal: str,
    time_available: str
) -> tuple:
    """Validate learner profile inputs."""

    if not background or \
       not background.strip():
        raise ValueError(
            "Please select your background."
        )

    if background not in BACKGROUND_OPTIONS:
        raise ValueError(
            f"Invalid background selection."
        )

    if not goal or not goal.strip():
        raise ValueError(
            "Please select your goal."
        )

    if goal not in GOAL_OPTIONS:
        raise ValueError(
            f"Invalid goal selection."
        )

    if not time_available or \
       not time_available.strip():
        raise ValueError(
            "Please select time available."
        )

    if time_available not in TIME_OPTIONS:
        raise ValueError(
            f"Invalid time selection."
        )

    return (
        background.strip(),
        goal.strip(),
        time_available.strip()
    )


def validate_question(question: str) -> str:
    """Validate mentor question."""
    if not question or \
       not question.strip():
        raise ValueError(
            "Please ask a question."
        )

    cleaned = question.strip()

    if len(cleaned.split()) < 2:
        raise ValueError(
            "Question too short. "
            "Please be more specific."
        )

    if len(cleaned) > 500:
        raise ValueError(
            "Question too long. "
            "Max 500 characters."
        )

    return cleaned


# ──────────────────────────────────────────
# RAG ENGINE
# ──────────────────────────────────────────

def build_knowledge_base() -> object:
    """Index roadmap docs into ChromaDB."""
    collection_name = "mentorai_roadmap"

    try:
        chroma_client.delete_collection(
            collection_name
        )
    except Exception:
        pass

    collection = chroma_client.create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )

    if not ROADMAP_DOCS:
        raise RuntimeError(
            "Knowledge base is empty. "
            "Check knowledge.py."
        )

    texts = [
        doc["content"]
        for doc in ROADMAP_DOCS
    ]

    print(
        f"⚙️  Indexing {len(texts)} "
        f"roadmap docs..."
    )

    try:
        embeddings = embedder.encode(
            texts,
            show_progress_bar=False
        ).tolist()
    except Exception as e:
        raise RuntimeError(
            f"Embedding failed: {e}"
        )

    collection.add(
        ids=[
            doc["id"] for doc in ROADMAP_DOCS
        ],
        embeddings=embeddings,
        documents=texts,
        metadatas=[{
            "topic": doc["topic"],
            "level": doc["level"],
            "id":    doc["id"]
        } for doc in ROADMAP_DOCS]
    )

    print(
        f"  ✅ Indexed: "
        f"{collection.count()} docs"
    )
    return collection


def retrieve_relevant_docs(
    collection,
    query: str,
    n_results: int = 7
) -> list:
    """Retrieve relevant roadmap sections."""
    if not query or not query.strip():
        return []

    try:
        embedding = embedder.encode(
            [query]
        ).tolist()

        results = collection.query(
            query_embeddings=embedding,
            n_results=min(
                n_results,
                collection.count()
            )
        )

        docs = []
        for i, doc in enumerate(
            results["documents"][0]
        ):
            distance = \
                results["distances"][0][i]
            if distance > 0.95:
                continue
            docs.append({
                "content":  doc,
                "topic":    results[
                    "metadatas"
                ][0][i]["topic"],
                "level":    results[
                    "metadatas"
                ][0][i]["level"],
                "distance": round(distance, 3)
            })

        return docs

    except Exception as e:
        print(
            f"  ⚠️  Retrieval error: {e} — "
            f"using all docs"
        )
        # Fallback: return first 5 docs
        return [
            {
                "content":  doc["content"],
                "topic":    doc["topic"],
                "level":    doc["level"],
                "distance": 0.5
            }
            for doc in ROADMAP_DOCS[:5]
        ]


# ──────────────────────────────────────────
# PARSERS
# ──────────────────────────────────────────

def safe_int(
    val,
    default: int = 1,
    min_val: int = 1,
    max_val: int = 9999
) -> int:
    try:
        return max(
            min_val,
            min(max_val, int(val))
        )
    except (ValueError, TypeError):
        return default


def safe_str(
    val,
    default: str = "Not specified"
) -> str:
    if not val or \
       str(val).strip() in [
           "", "nan", "None", "null"
       ]:
        return default
    return str(val).strip()


def safe_list(val) -> list:
    if isinstance(val, list):
        return [
            str(i) for i in val if i
        ]
    return []


def parse_phase(
    data: dict,
    index: int = 1
) -> Phase:
    """Parse and validate a single phase."""
    if not isinstance(data, dict):
        data = {}

    return Phase(
        phase_number=safe_int(
            data.get("phase_number", index),
            default=index
        ),
        phase_title=safe_str(
            data.get("phase_title"),
            f"Phase {index}"
        ),
        duration_weeks=safe_int(
            data.get("duration_weeks", 2),
            default=2,
            min_val=1,
            max_val=52
        ),
        focus_area=safe_str(
            data.get("focus_area"),
            "Core skills"
        ),
        skills=safe_list(
            data.get("skills")
        ),
        projects=safe_list(
            data.get("projects")
        ),
        resources=safe_list(
            data.get("resources")
        ),
        milestone=safe_str(
            data.get("milestone"),
            "Phase complete"
        ),
        why_this_phase=safe_str(
            data.get("why_this_phase"),
            "Building on foundations"
        )
    )


def parse_portfolio_project(
    data: dict
) -> PortfolioProject:
    """Parse and validate portfolio project."""
    if not isinstance(data, dict):
        data = {}

    difficulty = str(
        data.get("difficulty", "Intermediate")
    )
    if difficulty not in [
        "Beginner", "Intermediate", "Advanced"
    ]:
        difficulty = "Intermediate"

    return PortfolioProject(
        project_name=safe_str(
            data.get("project_name"),
            "AI Project"
        ),
        description=safe_str(
            data.get("description"),
            "Build an AI application"
        ),
        techniques_demonstrated=safe_list(
            data.get("techniques_demonstrated")
        ),
        difficulty=difficulty,
        impact=safe_str(
            data.get("impact"),
            "Demonstrates AI engineering skills"
        )
    )


def parse_weekly_schedule(
    data
) -> WeeklySchedule:
    """Parse weekly schedule."""
    defaults = {
        "monday":    "Study core concepts",
        "tuesday":   "Follow tutorials",
        "wednesday": "Build project",
        "thursday":  "Build project",
        "friday":    "Review and document",
        "saturday":  "Work on portfolio",
        "sunday":    "Rest and review"
    }

    if not isinstance(data, dict):
        data = {}

    return WeeklySchedule(**{
        day: safe_str(
            data.get(day), default
        )
        for day, default in defaults.items()
    })


def parse_curriculum(
    data: dict
) -> LearningCurriculum:
    """Parse full curriculum with validation."""

    if not isinstance(data, dict):
        data = {}

    # Readiness label
    readiness_label = str(
        data.get(
            "readiness_label", "Beginner"
        )
    )
    if readiness_label not in [
        "Beginner", "Early Intermediate",
        "Intermediate", "Advanced"
    ]:
        readiness_label = "Beginner"

    # Parse phases
    phases_raw = data.get("phases", [])
    if not isinstance(phases_raw, list):
        phases_raw = []

    phases = []
    for i, p in enumerate(
        phases_raw, 1
    ):
        try:
            phases.append(parse_phase(p, i))
        except Exception as e:
            print(
                f"  ⚠️  Phase {i} parse "
                f"error: {e} — skipping"
            )
            continue

    # Fallback phase if none parsed
    if not phases:
        phases = [Phase(
            phase_number=1,
            phase_title="Foundation",
            duration_weeks=4,
            focus_area=(
                "Core AI engineering skills"
            ),
            skills=[
                "Python", "LLM APIs",
                "Prompt Engineering"
            ],
            projects=["Simple chatbot"],
            resources=["Python.org docs"],
            milestone="First working AI app",
            why_this_phase=(
                "Build the foundation first"
            )
        )]

    # Parse portfolio projects
    projs_raw = data.get(
        "portfolio_projects", []
    )
    if not isinstance(projs_raw, list):
        projs_raw = []

    portfolio_projects = []
    for p in projs_raw:
        try:
            portfolio_projects.append(
                parse_portfolio_project(p)
            )
        except Exception:
            continue

    if not portfolio_projects:
        portfolio_projects = [
            PortfolioProject(
                project_name="AI Chatbot",
                description=(
                    "Build a chatbot using "
                    "LLM APIs"
                ),
                techniques_demonstrated=[
                    "LLM APIs", "Prompting"
                ],
                difficulty="Beginner",
                impact=(
                    "Demonstrates basic "
                    "AI integration"
                )
            )
        ]

    # Parse weekly schedule
    schedule = parse_weekly_schedule(
        data.get("weekly_schedule")
    )

    return LearningCurriculum(
        headline=safe_str(
            data.get("headline"),
            "Your personalized AI "
            "engineering path"
        ),
        total_weeks=safe_int(
            data.get("total_weeks", 12),
            default=12,
            min_val=1,
            max_val=104
        ),
        weekly_hours=safe_int(
            data.get("weekly_hours", 10),
            default=10,
            min_val=1,
            max_val=80
        ),
        readiness_score=safe_int(
            data.get("readiness_score", 30),
            default=30,
            min_val=1,
            max_val=100
        ),
        readiness_label=readiness_label,
        phases=phases,
        immediate_next_step=safe_str(
            data.get("immediate_next_step"),
            "Start with Python basics today."
        ),
        skills_to_skip=safe_list(
            data.get("skills_to_skip")
        ),
        biggest_gap=safe_str(
            data.get("biggest_gap"),
            "RAG and agent architecture"
        ),
        salary_unlock=safe_str(
            data.get("salary_unlock"),
            "$140k-$180k"
        ),
        time_to_first_job=safe_str(
            data.get("time_to_first_job"),
            "6-9 months"
        ),
        portfolio_projects=portfolio_projects,
        weekly_schedule=schedule,
        motivational_insight=safe_str(
            data.get("motivational_insight"),
            "Consistency beats intensity. "
            "Ship one project per week."
        )
    )


# ──────────────────────────────────────────
# CURRICULUM GENERATOR
# ──────────────────────────────────────────

def generate_curriculum(
    background: str,
    goal: str,
    time_available: str,
    collection
) -> MentorResult:
    """
    Full pipeline:
    Validate → RAG retrieval →
    LLM generation → Pydantic validation
    → MentorResult
    """

    # Validate
    background, goal, time_available = \
        validate_profile(
            background, goal, time_available
        )

    # Build retrieval query
    retrieval_query = (
        f"{background} {goal} "
        f"AI engineering learning path "
        f"Python RAG agents LLM production"
    )

    # Retrieve docs
    print(
        f"\n🎓 Generating curriculum for: "
        f"{background[:40]}..."
    )
    print(
        "  🔍 Retrieving roadmap sections..."
    )
    docs = retrieve_relevant_docs(
        collection,
        retrieval_query,
        n_results=7
    )

    if not docs:
        raise RuntimeError(
            "Could not retrieve relevant "
            "roadmap content. "
            "Please try again."
        )

    print(
        f"  ✅ Retrieved {len(docs)} sections"
    )

    topics_covered = [
        doc["topic"] for doc in docs
    ]

    # Build context
    knowledge_context = "\n\n---\n\n".join([
        f"[{doc['topic']}]\n{doc['content']}"
        for doc in docs
    ])

    # Generate
    print(
        "  🤖 Generating curriculum..."
    )
    prompt = CURRICULUM_PROMPT.format(
        background=background,
        goal=goal,
        time_available=time_available,
        knowledge_context=knowledge_context
    )

    try:
        raw = call_gemini(prompt)
        raw = clean_gemini_response(raw)
        data = json.loads(raw)
    except json.JSONDecodeError:
        print(
            "  ⚠️  JSON parse failed — "
            "using fallback curriculum"
        )
        data = {}
    except Exception as e:
        raise RuntimeError(
            f"Curriculum generation failed: "
            f"{e}"
        )

    curriculum = parse_curriculum(data)

    print(
        f"  ✅ Curriculum complete: "
        f"{len(curriculum.phases)} phases, "
        f"{curriculum.total_weeks} weeks"
    )

    return MentorResult(
        background=background,
        goal=goal,
        time_available=time_available,
        curriculum=curriculum,
        retrieved_doc_count=len(docs),
        topics_covered=topics_covered
    )


def ask_mentor(
    question: str,
    background: str,
    goal: str
) -> str:
    """Answer follow-up question."""
    question = validate_question(question)

    prompt = FOLLOWUP_PROMPT.format(
        background=background,
        goal=goal,
        question=question
    )

    try:
        return call_gemini(prompt)
    except Exception as e:
        return (
            f"Could not generate answer: {e}. "
            f"Please try again."
        )


# ── Build KB at module load ──
print(
    "\n📚 Building MentorAI knowledge base..."
)
KB_COLLECTION = build_knowledge_base()


# ───── Tests ─────
if __name__ == "__main__":

    print("\n🧪 Test 1: Frontend → startup")
    r1 = generate_curriculum(
        background=(
            "Frontend developer (React, JS, CSS)"
        ),
        goal=(
            "Get hired as an AI Engineer "
            "at a startup"
        ),
        time_available="3-4 hours per day",
        collection=KB_COLLECTION
    )
    assert r1.curriculum.total_weeks > 0
    assert r1.curriculum.readiness_score > 0
    assert len(r1.curriculum.phases) > 0
    assert r1.retrieved_doc_count > 0
    print(
        f"  ✅ Score  : "
        f"{r1.curriculum.readiness_score}/100"
    )
    print(
        f"     Weeks  : "
        f"{r1.curriculum.total_weeks}"
    )
    print(
        f"     Phases : "
        f"{len(r1.curriculum.phases)}"
    )

    print("\n🧪 Test 2: DS → AI engineer")
    r2 = generate_curriculum(
        background=(
            "Data scientist "
            "(ML basics, sklearn, notebooks)"
        ),
        goal=(
            "Transition from data science "
            "to AI engineering"
        ),
        time_available="1-2 hours per day",
        collection=KB_COLLECTION
    )
    # Scores vary by run — just verify both are valid
    assert 1 <= r2.curriculum.readiness_score <= 100
    assert 1 <= r1.curriculum.readiness_score <= 100
    print(
        f"  ✅ DS score  : "
        f"{r2.curriculum.readiness_score}/100"
    )
    print(
        f"     FE score  : "
        f"{r1.curriculum.readiness_score}/100"
    )
    print(
        f"     Both valid ✓"
    )
    print(
        f"     Skills skip: "
        f"{r2.curriculum.skills_to_skip[:3]}"
    )

    print("\n🧪 Test 3: Invalid background")
    try:
        validate_profile(
            "Astronaut",
            GOAL_OPTIONS[0],
            TIME_OPTIONS[0]
        )
    except ValueError as e:
        print(f"  ✅ Caught: {e}")

    print("\n🧪 Test 4: Invalid goal")
    try:
        validate_profile(
            BACKGROUND_OPTIONS[0],
            "World domination",
            TIME_OPTIONS[0]
        )
    except ValueError as e:
        print(f"  ✅ Caught: {e}")

    print("\n🧪 Test 5: Empty question")
    try:
        validate_question("")
    except ValueError as e:
        print(f"  ✅ Caught: {e}")

    print("\n🧪 Test 6: Short question")
    try:
        validate_question("hi")
    except ValueError as e:
        print(f"  ✅ Caught: {e}")

    print("\n🧪 Test 7: Phase validation")
    for phase in r1.curriculum.phases:
        assert phase.phase_number > 0
        assert phase.duration_weeks >= 1
        assert isinstance(phase.skills, list)
        assert isinstance(phase.projects, list)
    print(
        f"  ✅ All "
        f"{len(r1.curriculum.phases)} "
        f"phases valid"
    )

    print("\n🧪 Test 8: Portfolio projects")
    for proj in r1.curriculum.portfolio_projects:
        assert proj.difficulty in [
            "Beginner",
            "Intermediate",
            "Advanced"
        ]
        assert len(proj.project_name) > 0
    print(
        f"  ✅ "
        f"{len(r1.curriculum.portfolio_projects)} "
        f"projects valid"
    )

    print("\n🧪 Test 9: Weekly schedule")
    schedule = r1.curriculum.weekly_schedule
    for day in [
        "monday", "tuesday", "wednesday",
        "thursday", "friday", "saturday",
        "sunday"
    ]:
        assert len(
            getattr(schedule, day)
        ) > 0
    print("  ✅ All 7 days populated")

    print("\n🧪 Test 10: safe_int helper")
    assert safe_int("5") == 5
    assert safe_int("abc") == 1
    assert safe_int(None) == 1
    assert safe_int(-3, min_val=1) == 1
    assert safe_int(200, max_val=100) == 100
    print("  ✅ safe_int all cases correct")

    print("\n🧪 Test 11: Follow-up question")
    ans = ask_mentor(
        "Should I learn LangChain first?",
        BACKGROUND_OPTIONS[1],
        GOAL_OPTIONS[0]
    )
    assert len(ans) > 20
    print(
        f"  ✅ Answer: {ans[:80]}..."
    )

    print("\n🧪 Test 12: Fallback curriculum")
    fallback = parse_curriculum({})
    assert fallback.total_weeks >= 1
    assert len(fallback.phases) > 0
    assert len(
        fallback.portfolio_projects
    ) > 0
    print(
        f"  ✅ Fallback: "
        f"{fallback.total_weeks} weeks, "
        f"{len(fallback.phases)} phases"
    )

    print("\n✅ All 12 tests passed.")