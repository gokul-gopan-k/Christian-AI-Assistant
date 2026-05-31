# Christian AI Assistant — Architecture

## Overview

A Retrieval-Augmented Generation (RAG) system built for Christian theological Q&A and image generation. Users interact through a Gradio web UI that talks to a FastAPI backend. The backend orchestrates safety checks, hybrid retrieval, LLM generation, memory, and citation verification before returning a response.

---

## System Diagram

```
User (Browser)
     │
     ▼
Gradio UI  (app/frontend/ui.py)
     │  HTTP POST /chat  or  /generate-image
     ▼
FastAPI Backend  (app/api/main.py)
     │
     ├── Safety Rules  ──────────────────────────────► Block / Pass
     │
     ├── Intent Detector  ───────────────────────────► Classify query type
     │
     ├── Hybrid Retriever  ──────────────────────────► FAISS (semantic) + BM25 (keyword)
     │        └── Reranker  ──────────────────────────► Cross-encoder final ranking
     │
     ├── Memory
     │        ├── Short-Term  (in-memory, last 10 turns)
     │        └── Long-Term   (SQLite — user profile facts)
     │
     ├── LLM Answer Generator  (Groq / Llama 3.3 70B)
     │
     ├── Citation Verifier  ─────────────────────────► Confidence check
     │
     └── Image Generator  ───────────────────────────► Pollinations AI (flux model)
```

---

## Module Breakdown

### `app/api/main.py` — FastAPI Entry Point
- `GET /health` — liveness probe
- `POST /chat` — full RAG pipeline
- `POST /generate-image` — image generation pipeline
- Initializes SQLite memory DB on startup via lifespan hook

### `app/services/chat_service.py` — Chat Orchestrator
Coordinates the full pipeline in order:
1. Safety check → reject if unsafe
2. Intent detection
3. Hybrid retrieval (top 20) → rerank (top 5)
4. Load short-term + long-term memory
5. Generate answer via LLM
6. Verify citations
7. Persist new memories
8. Return answer + sources

### `app/frontend/ui.py` — Gradio UI
Two tabs:
- **Chat** — conversational interface, displays answer + cited sources
- **Image Generation** — text prompt → generated Christian artwork

---

## Retrieval Pipeline

### `retrieval/hybrid.py` — Hybrid Search
Combines two retrieval signals with weighted fusion:
- **BM25** (keyword, `rank-bm25`) — weight 0.4
- **FAISS semantic search** (`BAAI/bge-base-en-v1.5` embeddings) — weight 0.6
- Both scores are min-max normalized before fusion
- Optional `tradition_filter` to scope results to a denomination

### `retrieval/rerank.py` — Cross-Encoder Reranker
- Model: `cross-encoder/ms-marco-MiniLM-L-6-v2`
- Final score = `0.7 × rerank_score + 0.3 × hybrid_score`
- Returns top-k most relevant chunks

### `retrieval/filters.py` — Tradition Filters
Filter retrieved docs by tradition: `Scripture`, `Catholic`, `Protestant`, `Orthodox`

### `faiss/build_faiss.py` — Index Builder
Offline script that:
1. Loads chunked JSON files from `data/chunks/`
2. Encodes with `BAAI/bge-base-en-v1.5`
3. Builds a FAISS `IndexFlatIP` (cosine similarity)
4. Saves index to `data/faiss/christianity.faiss` and metadata to `data/processed/metadata.json`

---

## Knowledge Base

Source data covers four traditions, ingested via `ingestion/`:

| Tradition | Ingestion Script |
|-----------|-----------------|
| Scripture (140+ translations) | `bible_extract_verses.py`, `bible_passages.py` |
| Catholic | `chunk_catholic.py` |
| Protestant | `chunk_protestant.py` |
| Orthodox | `chunk_orthothodox.py` |

Raw Bible data lives in `bible_databases/formats/` (CSV, JSON, SQL, Markdown — 140 translations).

---

## LLM Layer

### `llm/llm_client.py`
- Provider: **Groq API**
- Model: **Llama 3.3 70B Versatile**
- Temperature: 0.3 (low, for factual RAG behavior)

### `llm/prompts.py`
- `SYSTEM_PROMPT` — instructs the model to cite sources, distinguish traditions, never invent doctrine
- `ANSWER_TEMPLATE` — injects user profile, intent, conversation history, question, and retrieved context

### `llm/answer_generator.py`
Builds the full prompt and calls the LLM. Returns a plain text answer with `[ID]` citations.

---

## Memory System

| Layer | Storage | Scope |
|-------|---------|-------|
| Short-term | In-memory `defaultdict` | Last 10 messages per user session |
| Long-term | SQLite (`data/memory.db`) | Persistent user profile facts across sessions |

### `memory/memory_extractor.py`
Uses the LLM to detect if a user message contains a personal fact worth saving (e.g., "I'm Catholic", "I'm studying Revelation"). If yes, saves it to SQLite.

---

## Safety Layer

### `safety/safety_rules.py`
Regex-based pre-filter. Blocks queries matching:
- Self-harm patterns
- Hate speech patterns
- Violence patterns

### `image_generation/prompt_filter.py`
LLM-based image safety guardrail. Blocks prompts that:
- Depict religious figures offensively
- Include extremist or heretical framing
- Violate respectful Christian imagery standards

---

## Image Generation

### `image_generation/image_generator.py`
- Safety check first via `prompt_filter.py`
- Builds a structured prompt via `prompt_builder.py`
- Calls **Pollinations AI** (flux model) via HTTP GET
- Saves result as UUID-named PNG to `generated_images/`
- Falls back to alternate URL on failure

---

## Intent Detection

### `intent/intent_detector.py`
LLM classifies each query into one of:
`scripture_lookup`, `doctrine_question`, `denomination_comparison`, `apologetics`, `historical_question`, `prayer_request`, `personal_advice`, `greeting`, `image_request`, `memory_save`, `memory_recall`, `unsafe`

Intent is passed to the answer generator to shape the response style.

---

## Citation Verification

### `verification/citation_verifier.py`
After answer generation, the LLM verifies whether the answer is actually supported by the retrieved chunks. Returns a confidence score. If `supported: false`, a low-confidence warning is appended to the answer.

---

## Evaluation Framework

`evaluation/` contains an offline eval suite:
- **Retrieval metrics**: Recall@K, Precision@K, Hit Rate
- **Answer metrics**: ROUGE scores
- `eval_dataset.json` — gold Q&A pairs for benchmarking

Run with: `python run_eval.py`

---

## Infrastructure

- **Docker Compose** — two services: `backend` (port 8000) and `frontend` (port 7860)
- **Dockerfile** — Python 3.10-slim base
- **`.env`** — `GROQ_API_KEY`
