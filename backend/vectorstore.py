import os
import pickle
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

class VectorStoreManager:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001", 
            google_api_key=self.api_key
        )
        self.vectorstore = None
        self.index_path = "vectorstore/index.pkl"

    def create_vectorstore(self, documents):
        """Creates a FAISS vector store from a list of LangChain documents."""
        if not documents:
            return None
            
        # Create the vector store from the documents
        self.vectorstore = FAISS.from_documents(
            documents=documents, 
            embedding=self.embeddings
        )
        
        # Ensure the save directory exists
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        
        # Save the index to disk (for local persistence)
        self.vectorstore.save_local(os.path.dirname(self.index_path))
        
        return self.vectorstore

    def load_vectorstore(self):
        """Loads an existing FAISS vector store from disk."""
        if os.path.exists(os.path.dirname(self.index_path)):
            self.vectorstore = FAISS.load_local(
                os.path.dirname(self.index_path), 
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            return self.vectorstore
        return None

    def similarity_search(self, query, k=4):
        """Searches the vector store for the top k relevant documents."""
        if not self.vectorstore:
            return []
        return self.vectorstore.similarity_search(query, k=k)