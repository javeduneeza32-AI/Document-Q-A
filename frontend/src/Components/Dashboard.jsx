import React, { useState } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import '../App.css'; // Imports your beautiful dark theme

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8001";

// 100 Floating Tech Symbols (Generated once)
const techSymbols = ['✦', '◇', '▣', '◆', '✧', '⬡', '⛭', '⌘', '⏣', '⛶', '⊞', '⊟', '⊠', '⊡', '⟡', '❖', '⬟', '⬢', '⛣', '⨁', '⬡', '⎔', '⏥', '⧫'];
const backgroundIcons = Array.from({ length: 100 }, (_, i) => {
  return (
    <div key={i} className="futuristic-icon" style={{
      top: `${Math.random() * 100}%`, left: `${Math.random() * 100}%`,
      animationDelay: `${Math.random() * 30}s`, fontSize: `${0.8 + Math.random() * 1.8}rem`
    }}>{techSymbols[i % techSymbols.length]}</div>
  );
});

export default function Dashboard() {
    const { logout, role, token } = useAuth();
    const navigate = useNavigate();

    // --- UI STATE ---
    const [magicActive, setMagicActive] = useState(false);
    const [selectedFile, setSelectedFile] = useState(null);
    const [uploadStatus, setUploadStatus] = useState("");
    const [isUploading, setIsUploading] = useState(false);
    const [bookState, setBookState] = useState("idle"); // idle, scanning, querying, glow-active
    const [question, setQuestion] = useState("");
    const [answer, setAnswer] = useState("");
    const [isAsking, setIsAsking] = useState(false);

    // --- HANDLERS ---
    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    const triggerMagic = (duration) => {
        setMagicActive(true);
        setTimeout(() => setMagicActive(false), duration);
    };

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
            await axios.post(`${API_BASE_URL}/upload`, formData, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setUploadStatus("Uploaded successfully!");
            setBookState("glow-active");
            triggerMagic(1500);
        } catch (error) {
            setBookState("idle");
            setUploadStatus(
                error.response?.status === 401
                    ? "Session expired. Please log in again."
                    : "Upload failed."
            );
        } finally {
            setIsUploading(false);
        }
    };

    const handleAskQuestion = async () => {
        if (!question.trim()) return alert("Enter a question.");

        setIsAsking(true);
        setBookState("querying");
        setAnswer("Searching the archive...");

        try {
            const response = await axios.post(
                `${API_BASE_URL}/query`,
                { question: question },
                { headers: { Authorization: `Bearer ${token}` } }
            );
            triggerMagic(3000);
            setTimeout(() => {
                // Defensive: backend should always send a string, but guard
                // here too so a malformed response can never crash the app.
                const rawAnswer = response.data.answer;
                setAnswer(typeof rawAnswer === 'string' ? rawAnswer : JSON.stringify(rawAnswer));
                setBookState("glow-active");
                setIsAsking(false);
            }, 3000);
        } catch (err) {
            setAnswer(
                "Error: " +
                (err.response?.status === 401
                    ? "Session expired. Please log in again."
                    : err.response?.data?.detail || "Could not reach backend.")
            );
            setBookState("idle");
            setIsAsking(false);
        }
    };

    // --- RENDER ---
    return (
        <div className={`app-wrapper ${magicActive ? 'magic-active' : ''}`}>
            {/* 100 Floating Tech Symbols */}
            <div className="background-swarm">{backgroundIcons}</div>

            {/* Main Knowledge Archive Dashboard */}
            <div className="archive-container">
                <header className="archive-header">
                    <h1>Knowledge Archive</h1>
                    <div className="archive-status" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <span>Status: Ready</span>
                        {/* Integrated Logout Button */}
                        <button onClick={handleLogout} style={{ background: 'transparent', border: '1px solid #FF5555', color: '#FF5555', padding: '4px 12px', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold', fontSize: '0.8rem' }}>
                            Logout
                        </button>
                    </div>
                </header>

                {/* The Glowing Book */}
                <div className="book-container">
                    <div className={`holo-book ${bookState}`}>
                        <div style={{ fontSize: '2.5rem', color: '#8B5CF6' }}>☰</div>
                        <div className="book-title">{selectedFile ? selectedFile.name.replace('.pdf', '') : 'Upload your first document'}</div>
                        <div className="book-subtitle">{selectedFile ? `Archive entry • ${(selectedFile.size / 1000).toFixed(0)} KB` : 'Upload a PDF to get started'}</div>
                    </div>
                </div>

                {/* Interaction Panels */}
                <div className="archive-interaction">
                    <div className="cyber-panel">
                        <label className="cyber-panel-label">Add to Archive</label>
                        <input type="file" accept=".pdf" onChange={handleFileChange} className="custom-file-input" />
                        <button className="cyber-button" onClick={handleUpload} disabled={isUploading || !selectedFile}>
                            {isUploading ? "Processing..." : "Upload & Analyze"}
                        </button>
                        {uploadStatus && <div className={`status-text ${uploadStatus.includes('failed') || uploadStatus.includes('expired') ? 'status-error' : 'status-success'}`}>{uploadStatus}</div>}
                    </div>

                    <div className="cyber-panel">
                        <label className="cyber-panel-label">Ask a Question</label>
                        <div className="query-row">
                            <input type="text" className="query-input" placeholder="e.g. What are the key features?" value={question} onChange={(e) => setQuestion(e.target.value)} />
                            <button className="cyber-button" onClick={handleAskQuestion} disabled={isAsking || !selectedFile} style={{ width: 'auto', marginTop: '0', padding: '14px 30px' }}>
                                {isAsking ? "..." : "Search"}
                            </button>
                        </div>
                    </div>

                    <div className="output-screen">
                        <div className="output-text">
                            {answer ? (
                                typeof answer === 'string'
                                    ? <ReactMarkdown>{answer}</ReactMarkdown>
                                    : JSON.stringify(answer)
                            ) : "Ready to answer your questions."}
                        </div>
                    </div>
                </div>

                <div className="footer">
                    Crafted by <span>Uneeza Javed</span> — AI Student
                </div>
            </div>
        </div>
    );
}