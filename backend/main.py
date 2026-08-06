import os
import PyPDF2
import google.genai as genai  # <--- Uses the official client directly
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Load API Key from .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("!!!!!!!!!!!!!! CRITICAL ERROR: API KEY NOT FOUND IN .env !!!!!!!!!!!!!!")
else:
    print("✅ API Key successfully loaded from .env file.")

# 1. Initialize FastAPI
app = FastAPI()

# 2. CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Data Models
class QueryRequest(BaseModel):
    question: str

# 4. Storage for PDF content
pdf_text_chunks = []

# 5. TEST ENDPOINT
@app.get("/")
def read_root():
    return {"message": "FastAPI Backend is running!"}

# 6. UPLOAD ENDPOINT
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    global pdf_text_chunks
    try:
        pdf_reader = PyPDF2.PdfReader(file.file)
        all_text = ""
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                all_text += text + "\n"

        if not all_text.strip():
            raise HTTPException(status_code=400, detail="PDF appears to have no readable text.")

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        pdf_text_chunks = text_splitter.split_text(all_text)

        return {
            "message": "File uploaded and indexed successfully!",
            "filename": file.filename,
            "status": "success",
            "chunks_created": len(pdf_text_chunks)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

# 7. QUERY ENDPOINT (USING OFFICIAL GOOGLE CLIENT DIRECTLY)
@app.post("/query")
async def ask_question(request: QueryRequest):
    global pdf_text_chunks
    
    if not pdf_text_chunks:
        raise HTTPException(status_code=400, detail="No documents loaded. Please upload a PDF first.")
    
    try:
        # Initialize the official client (No LangChain wrapper, so no v1beta bug!)
        client = genai.Client(api_key=api_key)
        
        context = "\n\n".join(pdf_text_chunks)
        prompt = f"""
        You are a helpful AI assistant. Answer the user's question based ONLY on the context below. 
        If the answer isn't in the text, say you don't know.
        
        Context:
        {context}

        Question: {request.question}
        Answer:
        """
        
        # Call the official API
        response = client.models.generate_content(
            model='models/gemini-3.6-flash', 
            contents=prompt
        )
        
        return {
            "question": request.question,
            "answer": response.text,  # direct response from Google
            "status": "success"
        }
    except Exception as e:
        print(f"\n🔥🔥🔥 CRASH ERROR IN BACKEND: {e} 🔥🔥🔥\n")
        import traceback
        traceback.print_exc() 
        raise HTTPException(status_code=500, detail=f"AI Error: {str(e)}")