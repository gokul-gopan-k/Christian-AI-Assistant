# Christian AI Assistant

A Retrieval-Augmented Generation (RAG) AI assistant for Christian theology. Ask questions about Scripture, doctrine, church history, and apologetics — with answers grounded in sourced texts across Catholic, Protestant, and Orthodox traditions. Also generates Christian artwork from text prompts.

---

## Features

- **Theological Q&A** — answers grounded in retrieved Scripture and denominational sources, never invented
- **Multi-tradition awareness** — distinguishes and compares Catholic, Protestant, and Orthodox views
- **Hybrid retrieval** — combines BM25 keyword search and FAISS semantic search for accurate chunk retrieval
- **Cross-encoder reranking** — re-scores retrieved chunks for maximum relevance
- **Intent detection** — classifies queries (scripture lookup, doctrine, apologetics, prayer, etc.) to shape responses
- **Citation verification** — LLM verifies answers are supported by sources; flags low-confidence responses
- **Short-term memory** — maintains last 10 turns of conversation context per user
- **Long-term memory** — persists user profile facts (denomination, study focus) across sessions in SQLite
- **Christian image generation** — generates artwork via Pollinations AI with LLM-based safety guardrails
- **Safety filtering** — regex + LLM guardrails block harmful, offensive, or inappropriate requests
- **Evaluation suite** — offline ROUGE and retrieval metrics (Recall@K, Precision@K, Hit Rate)

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | Groq API — Llama 3.3 70B Versatile |
| Embeddings | `BAAI/bge-base-en-v1.5` (sentence-transformers) |
| Vector DB | FAISS (IndexFlatIP) |
| Keyword search | BM25 (rank-bm25) |
| Reranker | `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| Backend | FastAPI + Uvicorn |
| Frontend | Gradio |
| Memory DB | SQLite |
| Image generation | Pollinations AI (flux model) |
| Containerization | Docker + Docker Compose |

---

## Project Structure

```
├── app/
│   ├── api/main.py            # FastAPI routes (/chat, /generate-image, /health)
│   ├── services/chat_service.py  # RAG pipeline orchestrator
│   └── frontend/ui.py         # Gradio web UI
├── llm/
│   ├── llm_client.py          # Groq API client (Llama 3.3 70B)
│   ├── answer_generator.py    # Prompt builder + LLM caller
│   └── prompts.py             # System prompt + answer template
├── retrieval/
│   ├── hybrid.py              # BM25 + FAISS hybrid search
│   ├── rerank.py              # Cross-encoder reranker
│   └── filters.py             # Tradition-based filters
├── memory/
│   ├── short_term_memory.py   # In-memory conversation history
│   ├── persistent_memory.py   # SQLite read/write
│   ├── memory_db.py           # DB init + connection
│   └── memory_extractor.py    # LLM-based fact extraction
├── intent/intent_detector.py  # Query intent classification
├── safety/safety_rules.py     # Regex safety filter
├── verification/citation_verifier.py  # Answer grounding check
├── image_generation/
│   ├── image_generator.py     # Pollinations AI caller
│   ├── prompt_builder.py      # Image prompt template
│   └── prompt_filter.py       # LLM image safety guardrail
├── ingestion/                 # Data chunking scripts
├── faiss/build_faiss.py       # Offline FAISS index builder
├── evaluation/                # Retrieval + answer eval metrics
├── bible_databases/           # 140+ Bible translations (CSV/JSON/SQL)
├── data/                      # Chunks, FAISS index, metadata, SQLite DB
├── generated_images/          # Saved generated images
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env
```

---

## Prerequisites

- Python 3.10+
- A [Groq API key](https://console.groq.com/) (free tier available)
- Docker + Docker Compose (optional, for containerized setup)

---

## Setup

### 1. Clone the repo

```bash
git clone <your-repo-url>
cd <repo-folder>
```

### 2. Configure environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Build the FAISS index

This only needs to be done once. Make sure your chunked data files exist in `data/chunks/` first (run the ingestion scripts if needed).

```bash
python faiss/build_faiss.py
```

Expected output files:
- `data/faiss/christianity.faiss`
- `data/processed/metadata.json`

---

## Running Locally

You need two terminals — one for the backend, one for the frontend.

**Terminal 1 — Backend:**
```bash
uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 — Frontend:**
```bash
python app/frontend/ui.py
```

Then open your browser at `http://localhost:7860`

---

## Running with Docker

```bash
docker-compose up --build
```

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:7860`

---

## API Reference

### `GET /health`
Returns service status.

```json
{ "status": "healthy" }
```

### `POST /chat`
```json
{
  "user_id": "user123",
  "message": "What does the Bible say about forgiveness?"
}
```
Response:
```json
{
  "answer": "...",
  "sources": [
    { "id": "Matt.6.14", "source": "KJV" }
  ]
}
```

### `POST /generate-image`
```json
{ "prompt": "The baptism of Jesus in the Jordan River" }
```
Response:
```json
{
  "image_path": "generated_images/abc123.png",
  "error": null
}
```

---

## Data Ingestion

To rebuild the knowledge base from scratch:

```bash
# Extract Bible verses
python ingestion/bible_extract_verses.py
python ingestion/bible_passages.py

# Chunk denominational sources
python ingestion/chunk_catholic.py
python ingestion/chunk_protestant.py
python ingestion/chunk_orthothodox.py

# Rebuild FAISS index
python faiss/build_faiss.py
```

---

## Evaluation

Run the offline evaluation suite against `evaluation/eval_dataset.json`:

```bash
python run_eval.py
```

Metrics:
- Retrieval: Recall@K, Precision@K, Hit Rate
- Answer quality: ROUGE-1, ROUGE-2, ROUGE-L

---


