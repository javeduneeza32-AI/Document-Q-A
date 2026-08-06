import os
import shutil
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from rag import DocumentQASystem
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "documents"
os.makedirs(UPLOAD_DIR, exist_ok=True)

qa_system = DocumentQASystem()

class QueryRequest(BaseModel):
    question: str

@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    for f in os.listdir(UPLOAD_DIR):
        os.remove(os.path.join(UPLOAD_DIR, f))
    
    saved_paths = []
    for file in files:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(400, "Only PDFs allowed")
        path = os.path.join(UPLOAD_DIR, file.filename)
        with open(path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        saved_paths.append(path)
    
    msg = qa_system.load_and_index(saved_paths)
    return {"message": msg, "files": [os.path.basename(p) for p in saved_paths]}

@app.post("/query")
async def query_endpoint(request: QueryRequest):
    if not qa_system.vectorstore:
        raise HTTPException(400, "No documents loaded.")
    return qa_system.query(request.question)

@app.get("/")
async def root():
    return {"status": "Server is running!"}