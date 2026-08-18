import os
from typing import List, Dict

import google.generativeai as genai
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS


def _detect_embedding_model(api_key: str) -> str:
    """
    Asks Google directly which embedding model this API key can use,
    instead of hardcoding a name that Google may rename or retire later.
    Confirmed working name as of Aug 2026: models/gemini-embedding-001
    """
    preferred_order = [
        "models/gemini-embedding-001",
        "models/text-embedding-004",
        "models/embedding-001",
    ]
    try:
        genai.configure(api_key=api_key)
        available = [
            m.name for m in genai.list_models()
            if "embedContent" in m.supported_generation_methods
        ]
        if not available:
            raise RuntimeError("No embedding-capable models returned by ListModels.")

        for name in preferred_order:
            if name in available:
                return name
        return available[0]
    except Exception as e:
        print(f"[rag.py] WARNING: could not auto-detect embedding model ({e}). "
              f"Falling back to 'models/gemini-embedding-001'.")
        return "models/gemini-embedding-001"


class DocumentQASystem:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        embedding_model = _detect_embedding_model(api_key)
        print(f"[rag.py] Using embedding model: {embedding_model}")

        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=embedding_model,
            google_api_key=api_key,
        )
        self.llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash", temperature=0.2)
        self.vectorstore = None

    def load_and_index(self, pdf_paths: List[str]) -> str:
        all_docs = []
        for path in pdf_paths:
            loader = PyPDFLoader(path)
            docs = loader.load()
            for d in docs:
                d.metadata["source"] = os.path.basename(path)
                d.metadata["page"] = d.metadata.get("page", 0)
            all_docs.extend(docs)

        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        chunks = splitter.split_documents(all_docs)

        self.vectorstore = FAISS.from_documents(chunks, self.embeddings)
        self.vectorstore.save_local("faiss_index")
        return f"✅ Indexed {len(pdf_paths)} PDFs with {len(chunks)} chunks."

    def query(self, question: str) -> Dict:
        if not self.vectorstore:
            return {"answer": "❌ No documents loaded.", "sources": []}

        docs = self.vectorstore.similarity_search(question, k=4)

        context = "\n\n".join([
            f"Source: {d.metadata.get('source', 'unknown')}, Page: {d.metadata.get('page', 0) + 1}\n{d.page_content}"
            for d in docs
        ])

        prompt = f"""You are a professional document analyst providing precise, polished answers based strictly on the provided context.

Guidelines:
- Write in clear, formal, and confident prose — no casual language, filler, or unnecessary hedging.
- Be concise: prioritize the most relevant facts over exhaustive detail.
- Structure longer answers with short paragraphs or a brief bulleted list where it improves clarity — avoid excessive formatting.
- Cite the source file and page number for every factual claim, in the format (Source: filename, Page: X).
- If the answer is not present in the context, state plainly: "This information is not available in the provided documents."
- Do not speculate, editorialize, or add information beyond what the context supports.

Context:
{context}

Question: {question}

Answer:"""

        response = self.llm.invoke(prompt)

        # Gemini responses can sometimes return content as a list of parts
        # (including internal metadata like signatures) instead of a plain
        # string — extract only the actual text so nothing internal ever
        # reaches the frontend.
        raw_content = response.content
        if isinstance(raw_content, list):
            answer = "".join(
                part.get("text", "") if isinstance(part, dict) else str(part)
                for part in raw_content
            )
        else:
            answer = str(raw_content)

        sources = []
        seen = set()
        for d in docs:
            file_name = d.metadata.get("source", "unknown")
            page_num = d.metadata.get("page", 0) + 1
            key = f"{file_name}:p{page_num}"
            if key not in seen:
                sources.append({"file": file_name, "page": page_num})
                seen.add(key)

        return {"answer": answer, "sources": sources}