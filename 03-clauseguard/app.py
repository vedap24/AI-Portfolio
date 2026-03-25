import os
import re
import json
import time
import fitz
import chromadb
from pathlib import Path
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from google import genai
from models import ClauseRisk, ContractSummary, ContractReport
from prompts import RISK_SCANNER_PROMPT, CONTRACT_SUMMARY_PROMPT

load_dotenv()

# ── Load models once ──
print("⏳ Loading embedding model...")
embedder = SentenceTransformer("all-MiniLM-L6-v2")
print("✅ Embedding model ready")

# ── Clients ──
chroma_client = chromadb.Client()
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ── Gemini model to use ──
GEMINI_MODEL = "gemini-3.1-flash-lite-preview" # "gemini-3.1-flash-preview is also good but more expensive


def clean_gemini_response(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")
        lines = [l for l in lines
                 if not l.strip().startswith("```")]
        raw = "\n".join(lines).strip()
    return raw


def call_gemini_with_retry(
    prompt: str,
    retries: int = 3,
    wait: int = 60
) -> str:
    """
    Call Gemini with automatic retry on rate limit.
    Waits 60 seconds on 429 before retrying.
    """
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

            # Rate limit — wait and retry
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                if attempt < retries:
                    print(
                        f"\n⏳ Rate limit hit. "
                        f"Waiting {wait}s before retry "
                        f"(attempt {attempt + 1}/{retries})..."
                    )
                    time.sleep(wait)
                    continue

            # Other error — retry with shorter wait
            if attempt < retries:
                time.sleep(5)
                continue

    raise RuntimeError(
        f"Gemini API failed after {retries + 1} attempts. "
        f"Last error: {last_error}"
    )


def extract_text_from_pdf(pdf_path: str) -> dict:
    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError(
            f"Expected PDF file, got: {path.suffix}"
        )

    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > 50:
        raise ValueError(
            f"PDF too large: {size_mb:.1f}MB. Maximum: 50MB."
        )

    print(f"📄 Extracting: {path.name}")
    doc = fitz.open(str(path))
    full_text = ""
    pages = []

    for page_num, page in enumerate(doc, start=1):
        page_text = page.get_text("text").strip()
        if page_text:
            full_text += f"\n\n[PAGE {page_num}]\n{page_text}"
            pages.append({
                "page": page_num,
                "text": page_text,
                "char_count": len(page_text)
            })

    doc.close()

    if not full_text.strip():
        raise ValueError(
            "PDF appears to be scanned or image-based. "
            "ClauseGuard requires text-based PDFs. "
            "Try copying text from the PDF — if you can't, "
            "it's image-based."
        )

    if len(full_text.strip()) < 100:
        raise ValueError(
            "PDF contains very little text. "
            "Document may be incomplete or corrupted."
        )

    print(
        f"  ✅ {len(full_text)} chars "
        f"from {len(pages)} pages"
    )

    return {
        "full_text": full_text.strip(),
        "pages": pages,
        "page_count": len(pages),
        "file_name": path.name
    }


def chunk_contract(full_text: str, file_name: str) -> list:
    text = re.sub(r'\[PAGE \d+\]', '', full_text)
    raw_chunks = re.split(r'\n{2,}', text)

    chunks = []
    chunk_id = 0

    for raw in raw_chunks:
        cleaned = raw.strip()
        if len(cleaned) < 40:
            continue
        if cleaned.isdigit():
            continue
        if len(cleaned.split()) < 6:
            continue

        chunk_id += 1
        chunks.append({
            "id": f"chunk_{chunk_id}",
            "text": cleaned,
            "char_count": len(cleaned),
            "word_count": len(cleaned.split()),
            "source": file_name,
            "chunk_index": chunk_id
        })

    # Merge tiny chunks
    '''
    merged = []
    for chunk in chunks:
        if merged and chunk["char_count"] < 150:
            merged[-1]["text"] += " " + chunk["text"]
            merged[-1]["char_count"] += chunk["char_count"]
        else:
            merged.append(chunk)
    '''
    merged = []
    MAX_CHARS = 4000 # Example limit to stay safe from token errors

    for chunk in chunks:
        # Condition: Small chunk AND merged list empty kaadu AND merge chesina tharvatha limit daatadu
        if merged and chunk["char_count"] < 150 and (merged[-1]["char_count"] + chunk["char_count"] < MAX_CHARS):
            merged[-1]["text"] += " " + chunk["text"]
            merged[-1]["char_count"] += chunk["char_count"]
        else:
            merged.append(chunk)

    if not merged:
        raise ValueError(
            "No meaningful clauses found after chunking. "
            "Contract may be too short or poorly formatted."
        )

    print(
        f"  ✅ {len(merged)} chunks "
        f"(avg {sum(c['char_count'] for c in merged) // len(merged)}"
        f" chars)"
    )

    return merged


def embed_and_store(
    chunks: list,
    collection_name: str = "contract"
) -> object:
    try:
        chroma_client.delete_collection(collection_name)
    except Exception:
        pass

    collection = chroma_client.create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )

    print(f"⚙️  Embedding {len(chunks)} chunks...")
    texts = [chunk["text"] for chunk in chunks]
    embeddings = embedder.encode(
        texts,
        show_progress_bar=False
    ).tolist()

    collection.add(
        ids=[chunk["id"] for chunk in chunks],
        embeddings=embeddings,
        documents=texts,
        metadatas=[{
            "source": chunk["source"],
            "chunk_index": chunk["chunk_index"],
            "word_count": chunk["word_count"]
        } for chunk in chunks]
    )

    print(f"  ✅ {len(chunks)} chunks stored")
    return collection


def retrieve_relevant_chunks(
    collection,
    query: str,
    n_results: int = 5
) -> list:
    query_embedding = embedder.encode([query]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=min(n_results, collection.count())
    )

    chunks = []
    for i, doc in enumerate(results["documents"][0]):
        chunks.append({
            "text": doc,
            "chunk_index": results["metadatas"][0][i]["chunk_index"],
            "distance": round(results["distances"][0][i], 3)
        })

    return chunks


def ingest_contract(pdf_path: str) -> tuple:
    extracted = extract_text_from_pdf(pdf_path)
    chunks = chunk_contract(
        extracted["full_text"],
        extracted["file_name"]
    )
    collection = embed_and_store(chunks)
    return collection, extracted


def get_contract_summary(full_text: str) -> ContractSummary:
    snippet = full_text[:3000]
    prompt = CONTRACT_SUMMARY_PROMPT.format(
        contract_text=snippet
    )

    raw = call_gemini_with_retry(prompt)
    raw = clean_gemini_response(raw)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback if JSON parse fails
        return ContractSummary(
            contract_type="Unknown",
            parties=["Party A", "Party B"],
            key_obligations=["Review manually"],
            contract_duration="Not specified",
            governing_law="Not specified",
            overall_risk="MEDIUM"
        )

    if not isinstance(data.get("parties"), list):
        data["parties"] = ["Party A", "Party B"]
    if not isinstance(data.get("key_obligations"), list):
        data["key_obligations"] = []
    if data.get("overall_risk") not in ["HIGH","MEDIUM","LOW"]:
        data["overall_risk"] = "MEDIUM"
    for f in ["contract_type","contract_duration","governing_law"]:
        if not data.get(f):
            data[f] = "Not specified"

    return ContractSummary(**data)


def scan_clause(
    clause_text: str,
    context: str,
    chunk_index: int
) -> ClauseRisk:
    prompt = RISK_SCANNER_PROMPT.format(
        clause=clause_text,
        context=context
    )

    try:
        raw = call_gemini_with_retry(prompt)
        raw = clean_gemini_response(raw)
        data = json.loads(raw)

        if data.get("risk_level") not in \
           ["HIGH", "MEDIUM", "LOW", "NONE"]:
            data["risk_level"] = "LOW"

        valid_cats = [
            "IP Ownership", "Payment Terms", "Non-Compete",
            "Termination", "Liability", "Confidentiality",
            "Penalty", "Indemnification", "Jurisdiction", "Other"
        ]
        if data.get("risk_category") not in valid_cats:
            data["risk_category"] = "Other"

        if not isinstance(data.get("is_standard"), bool):
            data["is_standard"] = True

        for f in ["risk_summary", "plain_english",
                  "what_to_watch", "negotiation_tip"]:
            if not data.get(f):
                data[f] = "Review this clause manually."

        return ClauseRisk(
            **data,
            clause_text=clause_text[:300],
            chunk_index=chunk_index
        )

    except Exception:
        # Safe fallback — never crash the full scan
        return ClauseRisk(
            risk_level="LOW",
            risk_category="Other",
            risk_summary="Could not analyze this clause.",
            plain_english=clause_text[:200],
            what_to_watch="Review this clause manually.",
            negotiation_tip="Consult a lawyer for this clause.",
            is_standard=True,
            clause_text=clause_text[:300],
            chunk_index=chunk_index
        )


def scan_full_contract(pdf_path: str) -> ContractReport:
    # Step 1: Ingest
    collection, extracted = ingest_contract(pdf_path)

    # Step 2: Summarize
    print("🤖 Summarizing contract...")
    summary = get_contract_summary(extracted["full_text"])
    context_str = (
        f"Contract type: {summary.contract_type}. "
        f"Parties: {', '.join(summary.parties)}. "
        f"Duration: {summary.contract_duration}."
    )

    # Step 3: Get all chunks
    all_chunks = collection.get(
        include=["documents", "metadatas"]
    )
    documents = all_chunks["documents"]
    metadatas = all_chunks["metadatas"]

    print(f"🔍 Scanning {len(documents)} clauses...")

    # Step 4: Scan each clause
    clause_risks = []
    for i, (doc, meta) in enumerate(
        zip(documents, metadatas)
    ):
        print(
            f"   Clause {i+1}/{len(documents)}...",
            end="\r"
        )
        risk = scan_clause(
            clause_text=doc,
            context=context_str,
            chunk_index=meta.get("chunk_index", i)
        )
        clause_risks.append(risk)
        time.sleep(20)  # 20s gap — prevents free tier rate limit

    print(f"\n✅ Scanned {len(clause_risks)} clauses")

    # Step 5: Count + sort
    high   = sum(1 for r in clause_risks
                 if r.risk_level == "HIGH")
    medium = sum(1 for r in clause_risks
                 if r.risk_level == "MEDIUM")
    low    = sum(1 for r in clause_risks
                 if r.risk_level in ["LOW", "NONE"])

    risk_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2, "NONE": 3}
    clause_risks.sort(
        key=lambda x: risk_order.get(x.risk_level, 3)
    )

    return ContractReport(
        file_name=extracted["file_name"],
        summary=summary,
        clause_risks=clause_risks,
        high_risk_count=high,
        medium_risk_count=medium,
        low_risk_count=low,
        total_clauses_scanned=len(clause_risks)
    )


# ───── Tests ─────
if __name__ == "__main__":

    print("\n🧪 Test 1: Full scan")
    report = scan_full_contract("test_contract.pdf")
    print(f"  ✅ HIGH: {report.high_risk_count} | "
          f"MEDIUM: {report.medium_risk_count} | "
          f"LOW: {report.low_risk_count}")

    print("\n🧪 Test 2: File not found")
    try:
        scan_full_contract("ghost.pdf")
    except FileNotFoundError as e:
        print(f"  ✅ Caught: {e}")

    print("\n🧪 Test 3: Wrong file type")
    try:
        extract_text_from_pdf("test.docx")
    except (FileNotFoundError, ValueError) as e:
        print(f"  ✅ Caught: {e}")

    print("\n✅ All tests passed.")