# ─────────────────────────────────────────────────────────────────────────────
# File: ref-log.md (template)
# ─────────────────────────────────────────────────────────────────────────────
REF_LOG_MD = r"""
# Reference Log (ref-log.md)


Document all external sources, tools, and GenAI usage here.


## External Libraries / Tools
- LangChain docs: https://python.langchain.com/
- ChromaDB docs: https://docs.trychroma.com/
- Streamlit docs: https://docs.streamlit.io/
- pypdf docs: https://pypdf.readthedocs.io/


## Articles / Tutorials
- (Add any blog posts or examples you consulted)


## GenAI Usage
- **ChatGPT** was used to scaffold the Streamlit + LangChain + Chroma structure and to propose chunking & retrieval settings. Rationale: accelerate boilerplate and focus on evaluation and UI polish.
- Prompts included: “build a Streamlit RAG app with Chroma”, “how to cite PDF page numbers in LangChain docs”.


## Design Notes
- Chosen chunker: `RecursiveCharacterTextSplitter` (size=1000, overlap=150) for robustness to formatting.
- Retrieval k=4 by default; **MMR** enabled for diversity.
- LLM temperature=0.1 to reduce hallucination and keep answers grounded.


"""