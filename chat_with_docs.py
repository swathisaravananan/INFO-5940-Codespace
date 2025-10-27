# ─────────────────────────────────────────────────────────────────────────────
# 📄 chat_with_docs.py — RAG Chat App using Streamlit + LangChain + Chroma
# Cornell INFO 5940 — LiteLLM proxy (https://api.ai.it.cornell.edu/)
# Safe: Reads API key from env or Codespaces secrets
# ─────────────────────────────────────────────────────────────────────────────

import io
import os
import uuid
from typing import List, Dict, Any

import streamlit as st
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from pypdf import PdfReader

# ─────────────────────────────────────────────────────────────────────────────
# ENV + UI CONFIG
# ─────────────────────────────────────────────────────────────────────────────
load_dotenv()  # loads .env or Codespaces secrets

st.set_page_config(page_title="RAG Chat", page_icon="📚", layout="wide")
st.title("📚 Retrieval-Augmented Chat with Your Documents")
st.caption("Upload .txt/.pdf → chunk → embed → query via Streamlit + LangChain + Chroma.")

# ─────────────────────────────────────────────────────────────────────────────
# EMBEDDINGS + LLM SETUP
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_embeddings():
    """Return embedding model configured via Cornell proxy."""
    backend = os.getenv("EMBEDDINGS_BACKEND", "openai").lower()
    if backend == "sentence":
        model = os.getenv("EMBEDDINGS_MODEL", "all-MiniLM-L6-v2")
        return HuggingFaceEmbeddings(model_name=model)

    model = os.getenv("EMBEDDINGS_MODEL", "openai.text-embedding-3-small")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.ai.it.cornell.edu/")
    api_key = os.getenv("OPENAI_API_KEY")
    return OpenAIEmbeddings(model=model, base_url=base_url, api_key=api_key)


@st.cache_resource(show_spinner=False)
def get_llm():
    """Return ChatOpenAI instance for Cornell proxy."""
    model = os.getenv("LLM_MODEL", "openai.gpt-4.1-mini")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.ai.it.cornell.edu/")
    api_key = os.getenv("OPENAI_API_KEY")
    return ChatOpenAI(model=model, temperature=0.1, base_url=base_url, api_key=api_key)

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def new_session_id() -> str:
    return str(uuid.uuid4())[:8]


def extract_txt(file_bytes: bytes) -> str:
    return file_bytes.decode("utf-8", errors="ignore")


def extract_pdf(file_bytes: bytes) -> List[Document]:
    reader = PdfReader(io.BytesIO(file_bytes))
    docs = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if text.strip():
            docs.append(Document(page_content=text, metadata={"page": i + 1}))
    return docs


def files_to_documents(uploaded_files: List) -> List[Document]:
    """Convert uploaded PDFs/TXTs to LangChain Document list."""
    all_docs = []
    for f in uploaded_files:
        name = f.name
        ext = os.path.splitext(name)[1].lower()
        file_bytes = f.getvalue()
        if ext == ".txt":
            text = extract_txt(file_bytes)
            if text.strip():
                all_docs.append(Document(page_content=text, metadata={"source": name}))
        elif ext == ".pdf":
            pdf_docs = extract_pdf(file_bytes)
            for d in pdf_docs:
                d.metadata["source"] = name
            all_docs.extend(pdf_docs)
        else:
            st.warning(f"⚠️ Unsupported file type skipped: {name}")
    return all_docs


def chunk_documents(docs: List[Document], chunk_size: int, chunk_overlap: int) -> List[Document]:
    """Split docs into chunks for embedding."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""],
    )
    return splitter.split_documents(docs)


@st.cache_resource(show_spinner=False)
def build_vectorstore(session_ns: str, _docs: List[Document]):
    """Build persistent Chroma vector store for this session."""
    embeddings = get_embeddings()
    persist_dir = os.path.join(".chroma", session_ns)
    os.makedirs(persist_dir, exist_ok=True)
    vs = Chroma.from_documents(
        documents=_docs,
        embedding=embeddings,
        collection_name=f"rag-{session_ns}",
        persist_directory=persist_dir,
    )
    return vs


def pretty_source(md: Dict[str, Any]) -> str:
    source = md.get("source", "")
    page = md.get("page")
    return f"{source} (p.{page})" if page else source


def build_history(history_pairs: List):
    """Format chat history for prompt injection."""
    if not history_pairs:
        return ""
    return "\n".join(f"User: {u}\nAssistant: {a}" for u, a in history_pairs[-6:])

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR SETTINGS
# ─────────────────────────────────────────────────────────────────────────────
st.sidebar.header("⚙️ Settings")
session_ns = st.sidebar.text_input("Session namespace", value=new_session_id())
chunk_size = st.sidebar.slider("Chunk size", 300, 2000, 1000, 50)
chunk_overlap = st.sidebar.slider("Chunk overlap", 0, 400, 150, 10)
search_k = st.sidebar.slider("Retriever k", 2, 10, 4)
reindex = st.sidebar.button("🔁 Reset & Reindex")

# ─────────────────────────────────────────────────────────────────────────────
# FILE UPLOAD
# ─────────────────────────────────────────────────────────────────────────────
uploaded = st.file_uploader(
    "Upload .txt and .pdf files (multiple)",
    type=["txt", "pdf"],
    accept_multiple_files=True,
)

# Initialize history safely
if "history" not in st.session_state:
    st.session_state.history = []

if reindex:
    st.cache_resource.clear()
    st.session_state.history = []
    st.success("✅ Vector store cleared. Please re-upload files.")

if uploaded:
    with st.spinner("📄 Processing documents..."):
        raw_docs = files_to_documents(uploaded)
        for d in raw_docs:
            d.metadata.setdefault("source", "uploaded")
        chunks = chunk_documents(raw_docs, chunk_size, chunk_overlap)

    with st.spinner("⚙️ Building vector store..."):
        vs = build_vectorstore(session_ns, chunks)
        retriever = vs.as_retriever(search_kwargs={"k": search_k})
else:
    retriever = None

# ─────────────────────────────────────────────────────────────────────────────
# RAG CHAIN
# ─────────────────────────────────────────────────────────────────────────────
system_prompt = (
    "You are a helpful assistant that answers ONLY using the provided context. "
    "If the answer is not in the context, say you don't know. "
    "Always cite sources (filename and page)."
)

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "Question: {question}\n\nContext:\n{context}\n\nChat history:\n{history}\n"),
])

llm = get_llm()


def format_docs(docs: List[Document]) -> str:
    blocks = []
    for d in docs:
        src = pretty_source(d.metadata)
        blocks.append(f"[Source: {src}]\n{d.page_content}")
    return "\n\n---\n\n".join(blocks)


if retriever:
    rag_chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough(),
            "history": lambda _: build_history(st.session_state.get("history", [])),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

# ─────────────────────────────────────────────────────────────────────────────
# CHAT INTERFACE
# ─────────────────────────────────────────────────────────────────────────────
user_q = st.chat_input("💬 Ask a question about your uploaded documents…")

for u, a in st.session_state.get("history", []):
    with st.chat_message("user"):
        st.markdown(u)
    with st.chat_message("assistant"):
        st.markdown(a)

if user_q:
    if not retriever:
        st.warning("⚠️ Upload at least one file to start.")
    else:
        with st.chat_message("user"):
            st.markdown(user_q)
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                answer = rag_chain.invoke(user_q)
                st.markdown(answer)
        st.session_state.history.append((user_q, answer))

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.write("\n\n---")
st.caption("Tip: Adjust chunking and retriever settings in sidebar. Reset clears cache.")
