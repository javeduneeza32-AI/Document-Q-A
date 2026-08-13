import os
import shutil
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from rag import DocumentQASystem

# New Imports for Auth
from database import get_db
from models import User, Document
from auth import get_current_user, get_current_admin_user, get_password_hash, create_access_token, verify_password

load_dotenv()

app = FastAPI()

# CORS - Add your Netlify URL here
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://document-q-a.netlify.app",
        "http://localhost:5173",
        "http://localhost:5174"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "documents"
os.makedirs(UPLOAD_DIR, exist_ok=True)

qa_system = DocumentQASystem()

class QueryRequest(BaseModel):
    question: str

# ---------------- FIXED AUTH MODELS & ENDPOINTS ----------------
class SignupRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/auth/signup")
async def signup(data: SignupRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter((User.username == data.username) | (User.email == data.email)).first()
    if existing_user:
        raise HTTPException(400, "Username or email already registered")
    hashed = get_password_hash(data.password)
    new_user = User(username=data.username, email=data.email, hashed_password=hashed, role="user")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}

@app.post("/auth/login")
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    token = create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer", "role": user.role}

# ------------------ ADMIN ENDPOINT ------------------
@app.get("/admin/users")
async def get_all_users(current_admin: User = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [{"id": u.id, "username": u.username, "email": u.email, "role": u.role} for u in users]

# ------------------ APP CORE ENDPOINTS ------------------
@app.post("/upload")
async def upload_file(file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    for f in os.listdir(UPLOAD_DIR):
        os.remove(os.path.join(UPLOAD_DIR, f))
    
    if not file.filename.endswith(".pdf"):
        raise HTTPException(400, "Only PDFs allowed")
        
    path = os.path.join(UPLOAD_DIR, file.filename)
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    msg = qa_system.load_and_index([path])
    new_doc = Document(filename=file.filename, user_id=current_user.id)
    db.add(new_doc)
    db.commit()
    
    return {"message": msg, "filename": os.path.basename(path)}

@app.post("/query")
async def query_endpoint(request: QueryRequest, current_user: User = Depends(get_current_user)):
    if not qa_system.vectorstore:
        raise HTTPException(400, "No documents loaded.")
    return qa_system.query(request.question)

@app.get("/")
async def root():
    return {"status": "Server is running!"}