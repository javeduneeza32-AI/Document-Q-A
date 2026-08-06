import React, { useState } from "react";
import axios from "axios";
import "./App.css";

// Change this to your live Render backend URL once deployed!
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8001";

// A list of mature, high-tech geometric symbols
const techSymbols = ['✦', '◇', '▣', '◆', '✧', '⬡', '⛭', '⌘', '⏣', '⛶', '⊞', '⊟', '⊠', '⊡', '⟡', '❖', '⬟', '⬢', '⛣', '⨁', '⬡', '⎔', '⏥', '⧫'];

function App() {
  // --- STATE ---
  const [phase, setPhase] = useState("intro");
  const [magicActive, setMagicActive] = useState(false);

  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [bookState, setBookState] = useState("idle");

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [isAsking, setIsAsking] = useState(false);

  // --- GENERATE 100 MATURE ICONS DYNAMICALLY ---
  const backgroundIcons = Array.from({ length: 100 }, (_, i) => {
    const top = Math.random() * 100;
    const left = Math.random() * 100;
    const delay = Math.random() * 30;
    const size = 0.8 + Math.random() * 1.8; // between 0.8rem and 2.6rem
    const symbol = techSymbols[i % techSymbols.length];
    return (
      <div
        key={i}
        className="futuristic-icon"
        style={{
          top: `${top}%`,
          left: `${left}%`,
          animationDelay: `${delay}s`,
          fontSize: `${size}rem`,
        }}
      >
        {symbol}
      </div>
    );
  });

  // --- HANDLERS ---
  const handleEnterArchive = () => setPhase("archive");

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setUploadStatus("");
      setAnswer("");
      setBookState("idle");
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return alert("Please select a file.");
    setIsUploading(true);
    setBookState("scanning");
    setUploadStatus("Processing...");

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      await axios.post(`${API_BASE_URL}/upload`, formData);
      setUploadStatus("Uploaded successfully!");
      setBookState("glow-active");
      triggerMagic(1500);
    } catch (error) {
      setBookState("idle");
      setUploadStatus("Upload failed.");
    } finally {
      setIsUploading(false);
    }
  };

  const triggerMagic = (duration) => {
    setMagicActive(true);
    setTimeout(() => setMagicActive(false), duration);
  };

  const handleAskQuestion = async () => {
    if (!question.trim()) return alert("Enter a question.");
    
    setIsAsking(true);
    setBookState("querying");
    setAnswer("Searching the archive...");

    try {
      const response = await axios.post(`${API_BASE_URL}/query`, { question: question });
      
      // TRIGGER THE MAGIC EFFECT (Flying icons speed up)
      triggerMagic(3000);
      
      // Wait for magic to finish, then display the answer
      setTimeout(() => {
        setAnswer(response.data.answer);
        setBookState("glow-active");
        setIsAsking(false);
      }, 3000);
      
    } catch (err) {
      setAnswer("Error: " + (err.response?.data?.detail || "Could not reach backend."));
      setBookState("idle");
      setIsAsking(false);
    }
  };

  // --- RENDER ---
  return (
    <div className={`app-wrapper ${magicActive ? 'magic-active' : ''}`}>
      
      {/* 100 MATURE ICONS SPREAD ACROSS THE FULL SCREEN */}
      <div className="background-swarm">
        {backgroundIcons}
      </div>

      {/* PHASE 1: INTRO SCREEN */}
      {phase === 'intro' && (
        <div className="intro-screen">
          <h1>Knowledge Archive</h1>
          <h2>Crafted by Uneeza Javed — AI Student</h2>
          <p>
            Welcome to your personal AI librarian. Upload any document, 
            PDF, or research paper. I will instantly scan the text, 
            analyze it, and answer your questions with pinpoint accuracy.
          </p>
          <button className="intro-btn" onClick={handleEnterArchive}>
            Enter the Archive
          </button>
        </div>
      )}

      {/* PHASE 2: ARCHIVE DASHBOARD */}
      {phase === 'archive' && (
        <div className="archive-container">
          <header className="archive-header">
            <h1>Knowledge Archive</h1>
            <div className="archive-status">Status: Ready</div>
          </header>

          {/* THE GLOWING FLOATING BOOK */}
          <div className="book-container">
            <div className={`holo-book ${bookState}`}>
              <div style={{ fontSize: '2.5rem', color: '#8B5CF6' }}>☰</div>
              <div className="book-title">
                {selectedFile ? selectedFile.name.replace('.pdf', '') : 'Upload your first document'}
              </div>
              <div className="book-subtitle">
                {selectedFile 
                  ? `Archive entry • ${selectedFile.size < 1000000 ? (selectedFile.size / 1000).toFixed(0) + ' KB' : (selectedFile.size / 1000000).toFixed(1) + ' MB'}`
                  : 'Upload a PDF to get started'}
              </div>
            </div>
          </div>

          {/* INTERFACE PANELS */}
          <div className="archive-interaction">
            
            {/* Add to Archive Panel */}
            <div className="cyber-panel">
              <label className="cyber-panel-label">Add to Archive</label>
              <input 
                type="file" 
                accept=".pdf" 
                onChange={handleFileChange} 
                className="custom-file-input" 
              />
              <button 
                className="cyber-button" 
                onClick={handleUpload} 
                disabled={isUploading || !selectedFile}
              >
                {isUploading ? "Processing..." : "Upload & Analyze"}
              </button>
              {uploadStatus && (
                <div className={`status-text ${uploadStatus.includes('failed') || uploadStatus.includes('Error') ? 'status-error' : 'status-success'}`}>
                  {uploadStatus}
                </div>
              )}
            </div>

            {/* Ask a Question Panel */}
            <div className="cyber-panel">
              <label className="cyber-panel-label">Ask a Question</label>
              <div className="query-row">
                <input 
                  type="text" 
                  className="query-input" 
                  placeholder="e.g., What are the key features?" 
                  value={question} 
                  onChange={(e) => setQuestion(e.target.value)} 
                />
                <button 
                  className="cyber-button" 
                  onClick={handleAskQuestion} 
                  disabled={isAsking || !selectedFile} 
                  style={{ width: 'auto', marginTop: '0', padding: '14px 30px' }}
                >
                  {isAsking ? "..." : "Search"}
                </button>
              </div>
            </div>

            {/* Output Panel */}
            <div className="output-screen">
              <div className={`output-text ${answer && !answer.startsWith('Error') ? 'glow-answer' : ''}`}>
                {answer ? answer : "Ready to answer your questions."}
              </div>
            </div>

          </div>

          {/* YOUR BIO FOOTER */}
          <div className="footer">
            Crafted by <span>Uneeza Javed</span> — AI Student
          </div>
        </div>
      )}
    </div>
  );
}

export default App;