import os
import json
import time
import chromadb
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from google import genai
from knowledge_base import (
    KNOWLEDGE_BASE_DOCS,
    PRODUCT_NAME
)
from models import (
    SupportAnswer,
    EscalationTicket,
    SupportResponse
)
from prompts import (
    ANSWER_PROMPT,
    ESCALATION_PROMPT,
    CONFIDENCE_THRESHOLD
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
                        "⏳ Rate limit. Waiting 40s..."
                    )
                    time.sleep(40)
                    continue
            if attempt < retries:
                time.sleep(2)
                continue
    raise RuntimeError(
        f"Gemini API failed: {last_error}"
    )


# ──────────────────────────────────────────
# RAG ENGINE
# ──────────────────────────────────────────

def build_knowledge_base() -> object:
    collection_name = "supportsense_kb"
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

    if not KNOWLEDGE_BASE_DOCS:
        raise RuntimeError(
            "Knowledge base is empty. "
            "Add documents to knowledge_base.py"
        )

    texts = [
        doc["content"]
        for doc in KNOWLEDGE_BASE_DOCS
    ]

    print(
        f"⚙️  Indexing {len(texts)} KB docs..."
    )

    try:
        embeddings = embedder.encode(
            texts,
            show_progress_bar=False
        ).tolist()
    except Exception as e:
        raise RuntimeError(
            f"Embedding failed: {e}. "
            f"Check sentence-transformers install."
        )

    collection.add(
        ids=[
            doc["id"]
            for doc in KNOWLEDGE_BASE_DOCS
        ],
        embeddings=embeddings,
        documents=texts,
        metadatas=[{
            "category": doc["category"],
            "title":    doc["title"],
            "id":       doc["id"]
        } for doc in KNOWLEDGE_BASE_DOCS]
    )

    print(
        f"  ✅ KB indexed: "
        f"{collection.count()} docs"
    )
    return collection


def retrieve_relevant_docs(
    collection,
    query: str,
    n_results: int = 3
) -> list:
    if not query or not query.strip():
        return []

    try:
        query_embedding = embedder.encode(
            [query]
        ).tolist()

        results = collection.query(
            query_embeddings=query_embedding,
            n_results=min(
                n_results, collection.count()
            )
        )

        docs = []
        for i, doc in enumerate(
            results["documents"][0]
        ):
            distance = results["distances"][0][i]
            if distance > 0.8:
                continue
            docs.append({
                "content":  doc,
                "category": results[
                    "metadatas"
                ][0][i]["category"],
                "title":    results[
                    "metadatas"
                ][0][i]["title"],
                "distance": round(distance, 3)
            })

        return docs

    except Exception as e:
        print(
            f"⚠️  Retrieval error: {e} — "
            f"returning empty"
        )
        return []


# ──────────────────────────────────────────
# INTENT CLASSIFIER
# ──────────────────────────────────────────

INTENT_LABELS = {
    "answerable":         "KB can answer this",
    "escalate_billing":   "Billing dispute",
    "escalate_complaint": "Customer complaint",
    "escalate_technical": "Complex technical",
    "escalate_unknown":   "Outside KB scope",
    "spam":               "Spam or gibberish"
}

ESCALATION_KEYWORDS = {
    "escalate_billing": [
        "refund", "charge", "overcharged",
        "invoice wrong", "billing error",
        "dispute", "cancel subscription",
        "charged twice", "money back",
        "unauthorized charge"
    ],
    "escalate_complaint": [
        "terrible", "awful", "scam",
        "worst", "lawsuit", "lawyer",
        "furious", "disgusting",
        "demand compensation",
        "unacceptable", "outraged",
        "fraud", "stealing"
    ]
}


def classify_intent(
    query: str,
    retrieved_docs: list
) -> dict:
    # No docs = can't answer
    if not retrieved_docs:
        return {
            "intent":     "escalate_unknown",
            "confidence": 0.9,
            "reasoning":  (
                "No relevant KB content found."
            )
        }

    # Keyword check
    query_lower = query.lower()
    for intent, keywords in \
            ESCALATION_KEYWORDS.items():
        if any(
            kw in query_lower
            for kw in keywords
        ):
            return {
                "intent":     intent,
                "confidence": 0.85,
                "reasoning":  (
                    "Escalation keyword detected."
                )
            }

    # LLM classification
    docs_context = "\n".join([
        f"- [{d['category']}] {d['title']}"
        for d in retrieved_docs
    ])

    prompt = f"""
Classify this customer support message.
Return JSON ONLY.

{{
  "intent": "<answerable | escalate_billing | escalate_complaint | escalate_technical | escalate_unknown>",
  "confidence": <float 0.0-1.0>,
  "reasoning": "<one sentence>"
}}

Available KB docs:
{docs_context}

Message: "{query}"
"""

    try:
        raw = call_gemini(prompt)
        raw = clean_gemini_response(raw)
        data = json.loads(raw)

        valid = list(INTENT_LABELS.keys())
        if data.get("intent") not in valid:
            data["intent"] = "answerable"

        try:
            conf = float(
                data.get("confidence", 0.7)
            )
            data["confidence"] = max(
                0.0, min(1.0, conf)
            )
        except (ValueError, TypeError):
            data["confidence"] = 0.7

        if not data.get("reasoning"):
            data["reasoning"] = (
                "Classification complete."
            )

        return data

    except (json.JSONDecodeError, Exception):
        return {
            "intent":     "answerable",
            "confidence": 0.6,
            "reasoning":  "Fallback classification."
        }


# ──────────────────────────────────────────
# ANSWER GENERATOR
# ──────────────────────────────────────────

def generate_answer(
    query: str,
    retrieved_docs: list
) -> SupportAnswer:
    if not retrieved_docs:
        return SupportAnswer(
            answer=(
                "I don't have information about "
                "that in our knowledge base. "
                "Let me connect you with our "
                "support team."
            ),
            confidence="LOW",
            answered_fully=False,
            source_sections=[],
            follow_up_suggestions=[],
            missing_info="No relevant KB docs found"
        )

    kb_content = "\n\n---\n\n".join([
        f"[{doc['title']}]\n{doc['content']}"
        for doc in retrieved_docs
    ])

    prompt = ANSWER_PROMPT.format(
        product_name=PRODUCT_NAME,
        kb_content=kb_content,
        question=query
    )

    try:
        raw = call_gemini(prompt)
        raw = clean_gemini_response(raw)
        data = json.loads(raw)

        if data.get("confidence") not in \
           ["HIGH", "MEDIUM", "LOW"]:
            data["confidence"] = "MEDIUM"

        if not isinstance(
            data.get("answered_fully"), bool
        ):
            data["answered_fully"] = bool(
                data.get("answer") and
                "don't have information" not in
                data.get("answer", "").lower()
            )

        for field in [
            "source_sections",
            "follow_up_suggestions"
        ]:
            if not isinstance(
                data.get(field), list
            ):
                data[field] = []

        if not data.get("answer"):
            data["answer"] = (
                "I wasn't able to find a clear "
                "answer. Please contact "
                "support@flowdesk.com."
            )

        if not data.get("missing_info"):
            data["missing_info"] = ""

        return SupportAnswer(**data)

    except json.JSONDecodeError:
        return SupportAnswer(
            answer=(
                "I'm having trouble processing "
                "your question right now. "
                "Please try again or contact "
                "support@flowdesk.com."
            ),
            confidence="LOW",
            answered_fully=False,
            source_sections=[],
            follow_up_suggestions=[],
            missing_info="Parse error"
        )

    except Exception as e:
        raise RuntimeError(
            f"Answer generation failed: {e}"
        )


# ──────────────────────────────────────────
# ESCALATION TICKET CREATOR
# ──────────────────────────────────────────

ESCALATION_REASONS = {
    "escalate_billing": (
        "Customer has billing dispute "
        "or refund request"
    ),
    "escalate_complaint": (
        "Customer is expressing frustration "
        "or filing complaint"
    ),
    "escalate_technical": (
        "Complex technical issue beyond FAQ"
    ),
    "escalate_unknown": (
        "Question outside knowledge base scope"
    )
}

FALLBACK_TICKET = lambda query, intent: \
    EscalationTicket(
        ticket_summary=(
            f"Customer query requires "
            f"human review: "
            f"{query[:80]}"
        ),
        priority="MEDIUM",
        department="General",
        customer_sentiment="Neutral",
        issue_type="Other",
        suggested_resolution=(
            "Review customer message "
            "and respond appropriately."
        ),
        context_for_agent=(
            f"Intent: {intent}. "
            f"Message: {query[:200]}"
        ),
        estimated_resolution_time=(
            "1-2 business days"
        )
    )


def create_escalation_ticket(
    query: str,
    intent: str
) -> EscalationTicket:
    reason = ESCALATION_REASONS.get(
        intent,
        "Requires human review"
    )

    prompt = ESCALATION_PROMPT.format(
        reason=reason,
        message=query
    )

    try:
        raw = call_gemini(prompt)
        raw = clean_gemini_response(raw)
        data = json.loads(raw)

        # Validate all fields
        if data.get("priority") not in \
           ["URGENT", "HIGH", "MEDIUM", "LOW"]:
            data["priority"] = "MEDIUM"

        valid_depts = [
            "Billing", "Technical",
            "General", "Management"
        ]
        if data.get("department") \
           not in valid_depts:
            data["department"] = "General"

        valid_sentiments = [
            "Frustrated", "Neutral",
            "Angry", "Confused"
        ]
        if data.get("customer_sentiment") \
           not in valid_sentiments:
            data["customer_sentiment"] = "Neutral"

        string_fields = [
            "ticket_summary", "issue_type",
            "suggested_resolution",
            "context_for_agent",
            "estimated_resolution_time"
        ]
        for field in string_fields:
            if not data.get(field):
                data[field] = "Review manually."

        return EscalationTicket(**data)

    except json.JSONDecodeError:
        return FALLBACK_TICKET(query, intent)

    except Exception as e:
        print(
            f"⚠️  Ticket creation error: {e} — "
            f"using fallback"
        )
        return FALLBACK_TICKET(query, intent)


# ──────────────────────────────────────────
# MAIN HANDLER
# ──────────────────────────────────────────

def validate_query(query: str) -> str:
    """Validate and clean query input."""
    if not query or not query.strip():
        raise ValueError(
            "Please enter a support question."
        )

    cleaned = query.strip()

    if len(cleaned) < 3:
        raise ValueError(
            "Message too short. "
            "Please describe your issue."
        )

    if len(cleaned) > 1000:
        raise ValueError(
            "Message too long. "
            "Max 1000 characters."
        )

    # Basic spam check
    spam_patterns = [
        "aaaaa", "zzzzz", "xxxxx",
        "12345678", "asdfgh"
    ]
    if any(
        p in cleaned.lower()
        for p in spam_patterns
    ):
        raise ValueError(
            "Message appears to be spam. "
            "Please describe your actual issue."
        )

    return cleaned


def handle_support_query(
    query: str
) -> SupportResponse:
    """
    Full support pipeline:
    Validate → Retrieve → Classify →
    Answer or Escalate → SupportResponse
    """

    # Validate + clean
    query = validate_query(query)

    # Step 1: Retrieve
    retrieved_docs = retrieve_relevant_docs(
        KB_COLLECTION, query
    )

    # Step 2: Classify
    intent_result = classify_intent(
        query, retrieved_docs
    )
    intent     = intent_result["intent"]
    confidence = intent_result["confidence"]

    # Step 3: Route
    if intent == "answerable":
        answer = generate_answer(
            query, retrieved_docs
        )

        # Low confidence answer → escalate
        conf_map = {
            "HIGH": 0.9,
            "MEDIUM": 0.6,
            "LOW":  0.3
        }
        answer_conf = conf_map.get(
            answer.confidence, 0.5
        )

        if answer_conf < CONFIDENCE_THRESHOLD \
           or not answer.answered_fully:
            return SupportResponse(
                query=query,
                response_type="escalation",
                intent="escalate_unknown",
                intent_confidence=confidence,
                escalation=create_escalation_ticket(
                    query, "escalate_unknown"
                ),
                retrieved_docs=retrieved_docs,
                doc_count=len(retrieved_docs),
                product_name=PRODUCT_NAME
            )

        return SupportResponse(
            query=query,
            response_type="answer",
            intent=intent,
            intent_confidence=confidence,
            answer=answer,
            retrieved_docs=retrieved_docs,
            doc_count=len(retrieved_docs),
            product_name=PRODUCT_NAME
        )

    else:
        return SupportResponse(
            query=query,
            response_type="escalation",
            intent=intent,
            intent_confidence=confidence,
            escalation=create_escalation_ticket(
                query, intent
            ),
            retrieved_docs=retrieved_docs,
            doc_count=len(retrieved_docs),
            product_name=PRODUCT_NAME
        )


# ── Build KB at module load ──
print(
    f"\n📚 Building {PRODUCT_NAME} KB..."
)
KB_COLLECTION = build_knowledge_base()


# ───── Tests ─────
if __name__ == "__main__":

    print("\n🧪 Test 1: Pricing query")
    r1 = handle_support_query(
        "How much does the Pro plan cost?"
    )
    assert r1.response_type == "answer"
    assert r1.answer is not None
    assert r1.answer.confidence in [
        "HIGH", "MEDIUM", "LOW"
    ]
    print(
        f"  ✅ Type: {r1.response_type} | "
        f"Confidence: {r1.answer.confidence}"
    )

    print("\n🧪 Test 2: Billing escalation")
    r2 = handle_support_query(
        "I was charged twice, "
        "I want a refund now"
    )
    assert r2.response_type == "escalation"
    assert r2.intent == "escalate_billing"
    print(
        f"  ✅ Type: {r2.response_type} | "
        f"Priority: {r2.escalation.priority}"
    )

    print("\n🧪 Test 3: Complaint")
    r3 = handle_support_query(
        "This is terrible and unacceptable"
    )
    assert r3.response_type == "escalation"
    print(
        f"  ✅ Sentiment: "
        f"{r3.escalation.customer_sentiment}"
    )

    print("\n🧪 Test 4: Off-topic")
    r4 = handle_support_query(
        "What is the meaning of life?"
    )
    assert r4.response_type == "escalation"
    print(
        f"  ✅ Intent: {r4.intent}"
    )

    print("\n🧪 Test 5: Integration query")
    r5 = handle_support_query(
        "Can I connect FlowDesk with Slack?"
    )
    assert r5.response_type == "answer"
    print(
        f"  ✅ Answered: "
        f"{r5.answer.answered_fully}"
    )

    print("\n🧪 Test 6: Too short")
    try:
        handle_support_query("hi")
    except ValueError as e:
        print(f"  ✅ Caught: {e}")

    print("\n🧪 Test 7: Too long")
    try:
        handle_support_query("x" * 1001)
    except ValueError as e:
        print(f"  ✅ Caught: {e}")

    print("\n🧪 Test 8: Spam detection")
    try:
        handle_support_query("aaaaaaaaaa")
    except ValueError as e:
        print(f"  ✅ Caught: {e}")

    print("\n🧪 Test 9: Escalation fallback")
    ticket = FALLBACK_TICKET(
        "test query", "escalate_unknown"
    )
    assert ticket.priority == "MEDIUM"
    assert ticket.department == "General"
    print(
        f"  ✅ Fallback ticket: "
        f"{ticket.priority} priority"
    )

    print("\n✅ All 9 tests passed.")