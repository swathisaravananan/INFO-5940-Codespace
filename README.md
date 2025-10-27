# 📚 Assignment 1 — RAG Chat (Streamlit + LangChain + Chroma)

This project implements a Retrieval-Augmented Generation (RAG) application that lets users upload **.txt** and **.pdf** files, indexes them in **ChromaDB**, and chat with a **conversational interface** powered by **LangChain**.

> ✅ Built to run inside the provided Codespace template (`requirements.txt`, `.devcontainer`) and follows the assignment rubric.

---

## ✨ Features
- Multi-file upload: **.txt** and **.pdf**
- Efficient **chunking** with adjustable size/overlap (sidebar)
- **Chroma** vector store with **OpenAI** (or Sentence-Transformers) embeddings
- Conversational RAG with **citations** (filename + page for PDFs)
- Streamlit UI with chat history & reset/re-index button
- No API keys in repo (use environment variables / Codespace secrets)

---

## 🚀 Quick Start (Codespace)

1. **Fork** the class repository and create a branch for Assignment 1.
2. Open the **Codespace** for your fork and check out your branch.
3. Ensure the **devcontainer** builds (provided by instructor). If you modify it, document below.
4. Set secrets for your Codespace:
   - `OPENAI_API_KEY` — required (unless you switch to sentence-transformers embeddings and a local LLM)
   - Optional: `EMBEDDINGS_BACKEND` (`openai` | `sentence`), `EMBEDDINGS_MODEL`, `LLM_MODEL`
5. Install dependencies (if the container does not auto-install):
   ```bash
   pip install -r requirements.txt
   ```
6. Run the app:
   ```bash
   streamlit run chat_with_docs.py --server.port 7860 --server.address 0.0.0.0
   ```
7. Open the forwarded port in the Codespace UI and start chatting.

---

## 🔧 Configuration
- **Chunking:** Sidebar controls for chunk size (default 1000) and overlap (150)
- **Retriever:** `k` top chunks (default 4) and optional **MMR** for diversity
- **Embeddings:**
  - Default: `OpenAIEmbeddings(model="text-embedding-3-large")`
  - Alternative (no keys): set `EMBEDDINGS_BACKEND=sentence` and optionally `EMBEDDINGS_MODEL=all-MiniLM-L6-v2`
- **LLM:** Default `gpt-4o-mini` via `ChatOpenAI`. You may swap to another provider if allowed by your environment.

---

## 🧱 Architecture
- **Streamlit UI** → file upload, chat I/O, sliders
- **Ingestion** → `.txt` directly; `.pdf` parsed page-wise (pypdf) to preserve page metadata
- **Chunking** → `RecursiveCharacterTextSplitter`
- **Vector DB** → `Chroma` (persisted under `.chroma/<session_ns>`)
- **RAG Chain** → LCEL pipeline: `retriever → prompt → ChatOpenAI → StrOutputParser`
- **Citations** → Appends filename + page in the assistant answer

---

## 🧪 Testing Tips
- Upload a long PDF (100+ pages) and a few .txt files; tweak chunk size/overlap
- Ask multi-turn questions; verify answers are **grounded** in the sources
- Click **Reset & Reindex** if you change chunking parameters significantly

---

## 🔐 API Keys & Security
- **Do not** commit any keys. Use Codespace/Repo secrets or `.env` (ignored by git).
- This app reads `OPENAI_API_KEY` from the environment only.

---

## 📝 What I changed from the provided template
- **requirements.txt**: ensured the following packages exist (or equivalent in the template):
  - `streamlit`
  - `langchain`
  - `langchain-community`
  - `langchain-openai`
  - `chromadb`
  - `pypdf`
  - `tiktoken`
  - `sentence-transformers` (optional; only needed for `EMBEDDINGS_BACKEND=sentence`)
- **.devcontainer**: _No changes required_. If you modify Python version/system packages, note them here.

---

## ▶️ How to run (summary)
```bash
# In Codespace terminal
export OPENAI_API_KEY=***   # or set via Secrets UI
streamlit run chat_with_docs.py --server.port 7860 --server.address 0.0.0.0
```

---

## 🧾 License
MIT (or course default). See `LICENSE` if included.

"""
