# ──────────────────────────────────────────
# AI ENGINEERING ROADMAP KNOWLEDGE BASE
# Curated content on every major skill area.
# This is the RAG source of truth for MentorAI.
# ──────────────────────────────────────────

ROADMAP_DOCS = [
    {
        "id":       "kb_foundations",
        "topic":    "Python & Programming Foundations",
        "level":    "beginner",
        "content": (
            "Python foundations for AI engineering: "
            "data structures (lists, dicts, sets), "
            "functions and decorators, classes and OOP, "
            "file I/O, error handling with try/except, "
            "virtual environments with venv or conda, "
            "package management with pip. "
            "Essential libraries: NumPy for arrays, "
            "Pandas for data manipulation, "
            "Matplotlib for visualization. "
            "Key concepts: list comprehensions, "
            "generators, context managers, type hints. "
            "Timeline: 4-6 weeks for a complete beginner, "
            "1-2 weeks if you know another language. "
            "Resources: Python.org docs, "
            "Automate the Boring Stuff (free online), "
            "Real Python tutorials. "
            "Project: Build a data analysis script "
            "using Pandas on a public dataset."
        )
    },
    {
        "id":       "kb_apis",
        "topic":    "APIs and LLM Integration",
        "level":    "beginner",
        "content": (
            "Working with LLM APIs is the core "
            "skill of AI engineering in 2026. "
            "Key concepts: REST APIs, HTTP methods, "
            "JSON request/response format, "
            "authentication with API keys, "
            "rate limiting and retry logic, "
            "environment variables with python-dotenv. "
            "Primary APIs to learn: "
            "Anthropic Claude API, OpenAI API, "
            "Google Gemini API (all have free tiers). "
            "Key skills: prompt construction, "
            "system prompts vs user prompts, "
            "temperature and token settings, "
            "streaming responses, error handling. "
            "Libraries: requests, httpx, "
            "official SDK packages per provider. "
            "Timeline: 1-2 weeks. "
            "Project: Build a simple chatbot "
            "using any LLM API with conversation history."
        )
    },
    {
        "id":       "kb_prompt_engineering",
        "topic":    "Prompt Engineering",
        "level":    "beginner",
        "content": (
            "Prompt engineering is the highest ROI "
            "skill for AI engineers in 2026. "
            "Core techniques: zero-shot prompting, "
            "few-shot prompting with examples, "
            "chain-of-thought for reasoning tasks, "
            "system prompt design, "
            "output format specification (JSON, XML), "
            "negative constraints (tell it what NOT to do), "
            "role assignment, temperature tuning. "
            "Advanced techniques: "
            "self-consistency, tree of thoughts, "
            "ReAct pattern (reason + act), "
            "meta-prompting. "
            "Common mistakes: vague instructions, "
            "no output format specified, "
            "ignoring edge cases. "
            "Timeline: 2-3 weeks of daily practice. "
            "Project: Build a prompt that extracts "
            "structured JSON from unstructured text "
            "with 95%+ accuracy."
        )
    },
    {
        "id":       "kb_pydantic",
        "topic":    "Structured Output with Pydantic",
        "level":    "beginner",
        "content": (
            "Pydantic is essential for production "
            "AI systems. It validates LLM outputs "
            "and prevents runtime crashes. "
            "Core concepts: BaseModel definition, "
            "field types and defaults, "
            "field_validator decorators, "
            "model_validator for cross-field rules, "
            "Optional fields, List and Dict types, "
            "Enum for constrained values. "
            "In AI systems: use Pydantic to define "
            "expected output schema, parse LLM JSON "
            "responses, validate field types, "
            "provide safe defaults when LLM omits fields. "
            "Pattern: prompt specifies JSON schema, "
            "LLM generates JSON, Pydantic validates. "
            "Timeline: 1 week. "
            "Project: Build a resume parser that "
            "extracts structured data from raw text "
            "using Pydantic validation."
        )
    },
    {
        "id":       "kb_rag",
        "topic":    "RAG — Retrieval Augmented Generation",
        "level":    "intermediate",
        "content": (
            "RAG is the most important production "
            "AI pattern in 2026. It grounds LLM "
            "responses in real documents. "
            "Core pipeline: chunk documents, "
            "embed chunks with sentence-transformers, "
            "store in vector DB (ChromaDB, Pinecone, Weaviate), "
            "embed query, retrieve top-k similar chunks, "
            "send chunks + query to LLM, "
            "LLM answers only from retrieved context. "
            "Key parameters: chunk size (256-512 tokens), "
            "overlap (50-100 tokens), "
            "top-k (3-5 chunks), "
            "similarity threshold. "
            "Chunking strategies: fixed-size, "
            "semantic, paragraph-based. "
            "Evaluation: precision, recall, "
            "faithfulness, answer relevance. "
            "Common failure modes: "
            "chunks too large (retrieval noise), "
            "chunks too small (missing context), "
            "wrong embedding model. "
            "Timeline: 2-3 weeks. "
            "Project: Build a document Q&A system "
            "on a set of PDFs with source citation."
        )
    },
    {
        "id":       "kb_agents",
        "topic":    "AI Agents and Tool Use",
        "level":    "intermediate",
        "content": (
            "AI agents are autonomous systems that "
            "plan, use tools, and achieve goals. "
            "Core patterns: "
            "ReAct (Reason + Act) — agent reasons "
            "about what to do, then acts with a tool, "
            "observes result, repeats. "
            "Tool use: functions the agent can call "
            "(web search, code execution, APIs, DB queries). "
            "Agent types: "
            "single agent with multiple tools, "
            "multi-agent with specialized roles, "
            "hierarchical agents (orchestrator + workers). "
            "State management: passing state between "
            "agent steps, managing conversation history. "
            "Frameworks: LangChain agents, LangGraph "
            "for stateful workflows, CrewAI for teams. "
            "Key challenges: infinite loops, "
            "tool errors, state corruption, cost control. "
            "Timeline: 3-4 weeks. "
            "Project: Build a research agent that "
            "searches the web and synthesizes a report."
        )
    },
    {
        "id":       "kb_vector_databases",
        "topic":    "Vector Databases",
        "level":    "intermediate",
        "content": (
            "Vector databases store and retrieve "
            "embeddings efficiently. "
            "Key concepts: embeddings are numerical "
            "representations of meaning, "
            "cosine similarity measures semantic closeness, "
            "ANN (Approximate Nearest Neighbor) search. "
            "Options by use case: "
            "ChromaDB — local, great for development, "
            "Pinecone — managed cloud, production-ready, "
            "Weaviate — open source, self-hosted, "
            "Qdrant — high performance, open source, "
            "pgvector — PostgreSQL extension. "
            "Key operations: upsert, query, delete, "
            "filter by metadata, namespace isolation. "
            "Embedding models: "
            "all-MiniLM-L6-v2 (fast, small), "
            "text-embedding-3-small (OpenAI), "
            "embed-english-v3 (Cohere). "
            "Timeline: 1-2 weeks. "
            "Project: Build semantic search over "
            "a large document collection."
        )
    },
    {
        "id":       "kb_fine_tuning",
        "topic":    "Fine-Tuning and Model Customization",
        "level":    "advanced",
        "content": (
            "Fine-tuning customizes a pretrained model "
            "on your specific data and task. "
            "When to fine-tune: "
            "when prompt engineering hits a ceiling, "
            "when you need consistent style/format, "
            "when latency matters (smaller fine-tuned "
            "model can outperform larger base model). "
            "When NOT to fine-tune: "
            "when RAG can solve it (cheaper, faster), "
            "when you have less than 100 examples, "
            "when the task changes frequently. "
            "Techniques: "
            "Full fine-tuning (expensive, most powerful), "
            "LoRA / QLoRA (parameter-efficient, popular), "
            "RLHF (reinforcement learning from human feedback), "
            "DPO (direct preference optimization). "
            "Platforms: Hugging Face, OpenAI fine-tuning API, "
            "Modal for GPU compute, RunPod. "
            "Timeline: 4-6 weeks including data collection. "
            "Project: Fine-tune a small model on "
            "domain-specific Q&A data."
        )
    },
    {
        "id":       "kb_mlops",
        "topic":    "MLOps and Production Deployment",
        "level":    "advanced",
        "content": (
            "MLOps bridges the gap between "
            "AI prototypes and production systems. "
            "Core areas: "
            "containerization with Docker, "
            "API serving with FastAPI, "
            "model versioning with MLflow or W&B, "
            "CI/CD pipelines for ML, "
            "monitoring for model drift, "
            "logging and observability, "
            "A/B testing for models. "
            "LLMOps specifics: "
            "prompt versioning, "
            "output logging for debugging, "
            "cost tracking per request, "
            "latency monitoring, "
            "hallucination detection. "
            "Tools: LangSmith for LangChain observability, "
            "Weights & Biases for experiment tracking, "
            "Arize for ML monitoring, "
            "Helicone for LLM observability. "
            "Deployment options: "
            "Streamlit Cloud (demos), "
            "Modal (serverless GPU), "
            "Hugging Face Spaces, "
            "AWS/GCP/Azure for enterprise. "
            "Timeline: 4-6 weeks. "
            "Project: Deploy a RAG system as "
            "a FastAPI endpoint with logging and monitoring."
        )
    },
    {
        "id":       "kb_evaluation",
        "topic":    "LLM Evaluation and Testing",
        "level":    "advanced",
        "content": (
            "Evaluating LLM applications is a "
            "core production skill often skipped "
            "by beginners. "
            "Evaluation dimensions: "
            "faithfulness (answers from context only), "
            "answer relevance (answers the question), "
            "context precision (retrieved chunks are relevant), "
            "context recall (right chunks retrieved). "
            "Evaluation approaches: "
            "LLM-as-judge (use GPT-4 to rate outputs), "
            "human evaluation (gold standard), "
            "automated metrics (BLEU, ROUGE for text gen), "
            "unit tests for structured outputs. "
            "Frameworks: RAGAS for RAG evaluation, "
            "DeepEval for LLM testing, "
            "PromptFoo for prompt testing. "
            "Red-teaming: adversarial inputs, "
            "jailbreaks, prompt injection attacks. "
            "Production evaluation: "
            "shadow mode testing, "
            "canary deployments, "
            "user feedback loops. "
            "Timeline: 2-3 weeks. "
            "Project: Build an evaluation harness "
            "for a RAG system using LLM-as-judge."
        )
    },
    {
        "id":       "kb_multimodal",
        "topic":    "Multimodal AI — Vision + Audio",
        "level":    "advanced",
        "content": (
            "Multimodal AI processes multiple data types. "
            "Vision: GPT-4 Vision, Claude 3 with images, "
            "Gemini Pro Vision for image understanding, "
            "document parsing from images, "
            "OCR with AI, chart and graph reading. "
            "Audio: OpenAI Whisper for speech-to-text, "
            "faster-whisper for local efficient transcription, "
            "ElevenLabs for text-to-speech, "
            "PyDub for audio manipulation. "
            "Voice pipelines: "
            "audio input → Whisper → LLM → TTS → audio output. "
            "Use cases: meeting transcription, "
            "voice agents, document understanding, "
            "image captioning, visual Q&A. "
            "Key challenge: latency optimization "
            "for real-time voice pipelines. "
            "Timeline: 2-3 weeks. "
            "Project: Build a voice-to-structured-data "
            "pipeline for field report capture."
        )
    },
    {
        "id":       "kb_system_design",
        "topic":    "AI System Design",
        "level":    "advanced",
        "content": (
            "AI system design is the senior-level skill "
            "that commands highest salaries. "
            "Core patterns: "
            "RAG for knowledge grounding, "
            "agents for autonomous task completion, "
            "chains for sequential processing, "
            "caching for cost/latency reduction, "
            "human-in-the-loop for safety. "
            "Design decisions: "
            "when to use RAG vs fine-tuning, "
            "when to use agents vs chains, "
            "how to handle context window limits, "
            "how to manage state across turns, "
            "how to design for observability. "
            "Scalability considerations: "
            "async processing for high volume, "
            "queue-based architectures, "
            "load balancing across LLM providers, "
            "cost optimization strategies. "
            "Interview preparation: "
            "practice designing systems end-to-end, "
            "explain tradeoffs explicitly, "
            "discuss failure modes and mitigations. "
            "Timeline: ongoing practice. "
            "Project: Design and implement a "
            "production-grade customer support AI "
            "with escalation logic."
        )
    },
    {
        "id":       "kb_career",
        "topic":    "AI Engineering Career Strategy",
        "level":    "all",
        "content": (
            "Breaking into AI engineering in 2026: "
            "Build in public — ship real projects, "
            "document what you learn, post on LinkedIn. "
            "Portfolio strategy: "
            "6-8 projects minimum, each demonstrating "
            "a different technique (RAG, agents, voice, "
            "structured output, fine-tuning). "
            "GitHub presence: "
            "clean READMEs, working demos, "
            "real data or realistic synthetic data. "
            "LinkedIn strategy: "
            "post about every project you ship, "
            "explain the technical decision behind "
            "each choice, use real industry statistics. "
            "Interview preparation: "
            "system design interviews for AI (RAG, agents), "
            "coding interviews still required at MAANG, "
            "be ready to explain every line of your projects. "
            "Target companies in 2026: "
            "AI-first startups (fastest learning), "
            "MAANG AI teams (best pay), "
            "enterprise AI teams (most openings). "
            "Salary ranges: "
            "$140k-$200k mid-level, "
            "$200k-$312k senior, "
            "56% wage premium over non-AI roles. "
            "Skills that differentiate: "
            "production experience over notebook demos, "
            "safety and evaluation mindset, "
            "full-stack thinking (prompt to deployment)."
        )
    }
]

BACKGROUND_OPTIONS = [
    "Complete beginner (no coding experience)",
    "Frontend developer (React, JS, CSS)",
    "Backend developer (Python, Java, Node)",
    "Data analyst (SQL, Excel, basic Python)",
    "Data scientist (ML basics, sklearn, notebooks)",
    "ML engineer (PyTorch, model training)",
    "Software engineer (general, any language)",
    "Product manager (no coding background)"
]

GOAL_OPTIONS = [
    "Get hired as an AI Engineer at a startup",
    "Get hired at MAANG as an AI Engineer",
    "Transition from data science to AI engineering",
    "Build my own AI SaaS product",
    "Add AI skills to my existing dev role",
    "Freelance on AI projects",
    "Build a portfolio to showcase AI skills"
]

TIME_OPTIONS = [
    "1-2 hours per day",
    "3-4 hours per day",
    "Full time (8+ hours per day)",
    "Weekends only (10-15 hours/week)"
]