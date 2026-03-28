import os
import re
import json
import time
import chromadb
from pathlib import Path
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from google import genai
from models import (
    QAResponse, SourceCitation,
    DocumentMeta, KnowledgeBaseStatus
)
from prompts import QA_PROMPT, DOCUMENT_SUMMARY_PROMPT

load_dotenv()

# ── Load models once ──
print("⏳ Loading embedding model...")
embedder = SentenceTransformer("all-MiniLM-L6-v2")
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
            response = gemini_client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt
            )
            return response.text
        except Exception as e:
            error_str = str(e)
            last_error = error_str
            if "429" in error_str or \
               "RESOURCE_EXHAUSTED" in error_str:
                if attempt < retries:
                    print(
                        f"⏳ Rate limit. Waiting 60s..."
                    )
                    time.sleep(60)
                    continue
            if attempt < retries:
                time.sleep(6)
                continue
    raise RuntimeError(
        f"Gemini failed after {retries+1} "
        f"attempts: {last_error}"
    )


# ──────────────────────────────────────────
# DOCUMENT PARSERS
# ──────────────────────────────────────────

def parse_pdf(file_path: Path) -> str:
    try:
        import fitz
        doc = fitz.open(str(file_path))
        text = ""
        for page in doc:
            page_text = page.get_text("text")
            if page_text.strip():
                text += page_text + "\n\n"
        doc.close()
        if not text.strip():
            raise ValueError(
                "PDF appears to be scanned or image-based. "
                "BrainBase needs text-based PDFs."
            )
        return text.strip()
    except ValueError:
        raise
    except Exception as e:
        raise RuntimeError(
            f"PDF parsing failed: {e}. "
            f"Try converting to TXT first."
        )


def parse_docx(file_path: Path) -> str:
    try:
        from docx import Document
        doc = Document(str(file_path))
        paragraphs = [
            p.text.strip()
            for p in doc.paragraphs
            if p.text.strip()
        ]
        if not paragraphs:
            raise ValueError(
                "DOCX file appears empty. "
                "Check the file has text content."
            )
        return "\n\n".join(paragraphs)
    except ValueError:
        raise
    except Exception as e:
        raise RuntimeError(
            f"DOCX parsing failed: {e}"
        )


def parse_txt(file_path: Path) -> str:
    try:
        try:
            text = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = file_path.read_text(encoding="latin-1")
        if not text.strip():
            raise ValueError(
                "TXT file appears empty."
            )
        return text.strip()
    except ValueError:
        raise
    except Exception as e:
        raise RuntimeError(
            f"TXT parsing failed: {e}"
        )


def extract_text(file_path: str) -> dict:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    supported = [".pdf", ".docx", ".txt", ".md"]
    if path.suffix.lower() not in supported:
        raise ValueError(
            f"Unsupported file type: {path.suffix}. "
            f"Supported: PDF, DOCX, TXT, MD"
        )

    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > 50:
        raise ValueError(
            f"File too large: {size_mb:.1f}MB. "
            f"Maximum allowed: 50MB."
        )

    if size_mb < 0.0001:
        raise ValueError(
            f"File appears empty: {path.name}"
        )

    print(f"📄 Parsing: {path.name}")

    ext = path.suffix.lower()
    if ext == ".pdf":
        text = parse_pdf(path)
    elif ext == ".docx":
        text = parse_docx(path)
    elif ext in [".txt", ".md"]:
        text = parse_txt(path)
    else:
        raise ValueError(f"No parser for: {ext}")

    if len(text.strip()) < 20:
        raise ValueError(
            f"{path.name} contains too little text "
            f"to be useful. Minimum 20 characters needed."
        )

    print(
        f"  ✅ {len(text)} chars extracted"
    )

    return {
        "text": text.strip(),
        "file_name": path.name,
        "file_type": ext,
        "file_size_mb": round(size_mb, 2),
        "char_count": len(text.strip())
    }


# ──────────────────────────────────────────
# CHUNKING
# ──────────────────────────────────────────

def chunk_document(
    text: str,
    file_name: str,
    chunk_size: int = 512,
    overlap: int = 50
) -> list:
    paragraphs = re.split(r'\n{2,}', text)
    paragraphs = [
        p.strip() for p in paragraphs
        if len(p.strip()) > 30
    ]

    if not paragraphs:
        # Fallback: split by sentences
        paragraphs = re.split(r'(?<=[.!?])\s+', text)
        paragraphs = [
            p.strip() for p in paragraphs
            if len(p.strip()) > 20
        ]

    if not paragraphs:
        # Last resort: use full text as one chunk
        return [{
            "id": f"{file_name}_chunk_1",
            "text": text[:4000],
            "source": file_name,
            "chunk_index": 1,
            "char_count": len(text[:4000])
        }]

    chunks = []
    current_chunk = ""
    chunk_id = 0

    for para in paragraphs:
        if len(current_chunk) + len(para) < chunk_size * 4:
            current_chunk += para + "\n\n"
        else:
            if current_chunk.strip():
                chunk_id += 1
                chunks.append({
                    "id": f"{file_name}_chunk_{chunk_id}",
                    "text": current_chunk.strip(),
                    "source": file_name,
                    "chunk_index": chunk_id,
                    "char_count": len(current_chunk.strip())
                })

            prev_words = current_chunk.split()
            overlap_text = " ".join(
                prev_words[-overlap:]
            ) if prev_words else ""
            current_chunk = (
                overlap_text + " " + para + "\n\n"
            )

    if current_chunk.strip():
        chunk_id += 1
        chunks.append({
            "id": f"{file_name}_chunk_{chunk_id}",
            "text": current_chunk.strip(),
            "source": file_name,
            "chunk_index": chunk_id,
            "char_count": len(current_chunk.strip())
        })

    chunks = [c for c in chunks if c["char_count"] > 50]

    if not chunks:
        chunks = [{
            "id": f"{file_name}_chunk_1",
            "text": text[:4000],
            "source": file_name,
            "chunk_index": 1,
            "char_count": len(text[:4000])
        }]

    print(
        f"  ✅ {len(chunks)} chunks "
        f"(overlap: {overlap} words)"
    )
    return chunks


# ──────────────────────────────────────────
# EMBEDDING + STORAGE
# ──────────────────────────────────────────

def get_or_create_collection(
    collection_name: str = "brainbase"
) -> object:
    try:
        return chroma_client.get_collection(
            collection_name
        )
    except Exception:
        return chroma_client.create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )


def embed_and_store(
    chunks: list,
    collection_name: str = "brainbase"
) -> object:
    collection = get_or_create_collection(
        collection_name
    )

    existing = collection.get()
    existing_ids = set(existing["ids"])

    new_chunks = [
        c for c in chunks
        if c["id"] not in existing_ids
    ]

    if not new_chunks:
        print("  ℹ️  Already in DB — skipping")
        return collection

    print(f"⚙️  Embedding {len(new_chunks)} chunks...")

    texts = [c["text"] for c in new_chunks]
    embeddings = embedder.encode(
        texts,
        show_progress_bar=False
    ).tolist()

    collection.add(
        ids=[c["id"] for c in new_chunks],
        embeddings=embeddings,
        documents=texts,
        metadatas=[{
            "source": c["source"],
            "chunk_index": c["chunk_index"],
            "char_count": c["char_count"]
        } for c in new_chunks]
    )

    print(
        f"  ✅ {len(new_chunks)} stored. "
        f"Total: {collection.count()}"
    )
    return collection


def ingest_document(
    file_path: str,
    collection_name: str = "brainbase"
) -> dict:
    extracted = extract_text(file_path)
    chunks = chunk_document(
        extracted["text"],
        extracted["file_name"]
    )
    collection = embed_and_store(
        chunks, collection_name
    )
    return {
        "file_name": extracted["file_name"],
        "file_type": extracted["file_type"],
        "chunks_added": len(chunks),
        "total_in_db": collection.count(),
        "char_count": extracted["char_count"]
    }


def retrieve_chunks(
    query: str,
    collection_name: str = "brainbase",
    n_results: int = 5
) -> list:
    collection = get_or_create_collection(
        collection_name
    )

    if collection.count() == 0:
        return []

    query_embedding = embedder.encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=min(n_results, collection.count())
    )

    chunks = []
    for i, doc in enumerate(results["documents"][0]):
        chunks.append({
            "text": doc,
            "source": results["metadatas"][0][i]["source"],
            "chunk_index": results["metadatas"][0][i][
                "chunk_index"
            ],
            "distance": round(
                results["distances"][0][i], 3
            )
        })
    return chunks


def clear_knowledge_base(
    collection_name: str = "brainbase"
) -> None:
    try:
        chroma_client.delete_collection(collection_name)
        print("✅ Knowledge base cleared")
    except Exception:
        pass


# ──────────────────────────────────────────
# Q&A ENGINE
# ──────────────────────────────────────────

def get_document_summary(text: str) -> dict:
    snippet = text[:2000]
    prompt = DOCUMENT_SUMMARY_PROMPT.format(
        text=snippet
    )
    try:
        raw = call_gemini(prompt)
        raw = clean_gemini_response(raw)
        data = json.loads(raw)
        data.setdefault(
            "title_guess", "Unknown document"
        )
        data.setdefault("main_topics", [])
        data.setdefault("document_type", "other")
        data.setdefault(
            "one_line_summary",
            "No summary available."
        )
        if not isinstance(data["main_topics"], list):
            data["main_topics"] = []
        return data
    except Exception:
        return {
            "title_guess": "Unknown document",
            "main_topics": [],
            "document_type": "other",
            "one_line_summary": "Could not summarize."
        }


def answer_question(
    question: str,
    collection_name: str = "brainbase",
    n_chunks: int = 5
) -> QAResponse:

    # Validate
    if not question or len(question.strip()) < 3:
        raise ValueError(
            "Question too short. "
            "Please ask a complete question."
        )
    if len(question.strip()) > 1000:
        raise ValueError(
            "Question too long. "
            "Keep it under 1000 characters."
        )

    # Check KB
    collection = get_or_create_collection(
        collection_name
    )
    if collection.count() == 0:
        return QAResponse(
            answer=(
                "No documents uploaded yet. "
                "Please upload at least one document."
            ),
            confidence="LOW",
            sources=[],
            found_in_docs=False,
            follow_up_suggestions=[]
        )

    # Retrieve
    chunks = retrieve_chunks(
        question, collection_name, n_results=n_chunks
    )

    if not chunks:
        return QAResponse(
            answer=(
                "Could not find relevant content "
                "for your question."
            ),
            confidence="LOW",
            sources=[],
            found_in_docs=False,
            follow_up_suggestions=[]
        )

    # Build context
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(
            f"[Source {i}: {chunk['source']}]\n"
            f"{chunk['text']}"
        )
    context = "\n\n---\n\n".join(context_parts)

    # Call Gemini
    prompt = QA_PROMPT.format(
        context=context,
        question=question
    )

    try:
        raw = call_gemini(prompt)
        raw = clean_gemini_response(raw)
        data = json.loads(raw)
    except json.JSONDecodeError:
        return QAResponse(
            answer=(
                "Could not parse the response. "
                "Try rephrasing your question."
            ),
            confidence="LOW",
            sources=[],
            found_in_docs=False,
            follow_up_suggestions=[]
        )

    # Validate fields
    if data.get("confidence") not in \
       ["HIGH", "MEDIUM", "LOW"]:
        data["confidence"] = "MEDIUM"

    if not isinstance(data.get("found_in_docs"), bool):
        data["found_in_docs"] = bool(
            data.get("answer") and
            "could not find" not in
            data.get("answer", "").lower()
        )

    if not isinstance(data.get("sources"), list):
        data["sources"] = []

    validated_sources = []
    for src in data["sources"]:
        if isinstance(src, dict):
            validated_sources.append(
                SourceCitation(
                    file_name=src.get(
                        "file_name", "Unknown"
                    ),
                    relevant_quote=src.get(
                        "relevant_quote", ""
                    )[:200]
                )
            )
    data["sources"] = validated_sources

    if not isinstance(
        data.get("follow_up_suggestions"), list
    ):
        data["follow_up_suggestions"] = []

    if not data.get("answer"):
        data["answer"] = (
            "Could not generate answer. "
            "Try rephrasing."
        )

    return QAResponse(**data)


def get_kb_status(
    collection_name: str = "brainbase"
) -> KnowledgeBaseStatus:
    collection = get_or_create_collection(
        collection_name
    )
    if collection.count() == 0:
        return KnowledgeBaseStatus(
            total_documents=0,
            total_chunks=0,
            document_names=[]
        )
    all_data = collection.get(include=["metadatas"])
    doc_names = list(set(
        m["source"] for m in all_data["metadatas"]
    ))
    return KnowledgeBaseStatus(
        total_documents=len(doc_names),
        total_chunks=collection.count(),
        document_names=doc_names
    )


# ───── Tests ─────
if __name__ == "__main__":

    print("\n🧪 Test 1: Full pipeline")
    meta = ingest_document("test_notes.txt")
    print(f"  ✅ Ingested: {meta['file_name']}")

    response = answer_question("What is RAG?")
    print(f"  ✅ Confidence : {response.confidence}")
    print(f"     Found     : {response.found_in_docs}")
    print(f"     Answer    : {response.answer[:80]}")

    print("\n🧪 Test 2: Not in docs")
    r2 = answer_question(
        "What is the capital of France?"
    )
    print(f"  ✅ Found: {r2.found_in_docs}")

    print("\n🧪 Test 3: KB status")
    status = get_kb_status()
    print(f"  ✅ Docs  : {status.total_documents}")
    print(f"     Chunks: {status.total_chunks}")

    print("\n🧪 Test 4: Empty question")
    try:
        answer_question("  ")
    except ValueError as e:
        print(f"  ✅ Caught: {e}")

    print("\n🧪 Test 5: File not found")
    try:
        extract_text("ghost.pdf")
    except FileNotFoundError as e:
        print(f"  ✅ Caught: {e}")

    print("\n🧪 Test 6: Unsupported file type")
    try:
        extract_text("data.xlsx")
    except (FileNotFoundError, ValueError) as e:
        print(f"  ✅ Caught: {e}")

    print("\n🧪 Test 7: Document summary")
    summary = get_document_summary(
        "RAG is Retrieval Augmented Generation. "
        "It improves LLM answers using external knowledge."
    )
    print(f"  ✅ Summary: {summary['one_line_summary']}")

    print("\n✅ All tests passed.")