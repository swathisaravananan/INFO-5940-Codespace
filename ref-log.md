
# Reference Log (ref-log.md)


Documenting all external sources, tools, and GenAI usage here.


## External Libraries / Tools
- LangChain docs: https://python.langchain.com/
- ChromaDB docs: https://docs.trychroma.com/
- Streamlit docs: https://docs.streamlit.io/
- pypdf docs: https://pypdf.readthedocs.io/


## Articles / Tutorials
- (Add any blog posts or examples you consulted)


## GenAI Usage
- Used ChatGPT sparingly for debugging Streamlit setup and verifying LangChain–Chroma integration steps.  
- Primarily relied on class examples and official documentation for implementation.  
- Prompts were limited to clarifying syntax and confirming correct use of `RecursiveCharacterTextSplitter` and PDF citation handling.



## Design Notes
- Chosen chunker: `RecursiveCharacterTextSplitter` (size=1000, overlap=150) for robustness to formatting.
- Retrieval k=4 by default; **MMR** enabled for diversity.
- LLM temperature=0.1 to reduce hallucination and keep answers grounded.


"""
