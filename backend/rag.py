import os
from typing import List, Dict

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS

class DocumentQASystem:
    def __init__(self):
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2)
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

        prompt = f"""You are a document assistant. Answer ONLY using the context below.
If the answer is NOT in the context, say "I couldn't find that in the documents."
ALWAYS cite the source file and page number.

Context:
{context}

Question: {question}

Answer:"""

        response = self.llm.invoke(prompt)
        answer = response.content

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