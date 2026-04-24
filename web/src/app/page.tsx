"use client";

import React, { useState, useEffect } from 'react';
import { Upload, FileText, Zap, Loader2, Download, Sparkles, BrainCircuit, Type } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function AutoNotesDashboard() {
  const [file, setFile] = useState<File | null>(null);
  const [rawText, setRawText] = useState('');
  const [inputMode, setInputMode] = useState<'upload' | 'text'>('upload');
  const [status, setStatus] = useState<'idle' | 'processing' | 'completed' | 'error'>('idle');
  const [jobId, setJobId] = useState<string | null>(null);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) return;

    setFile(selectedFile);
    setStatus('processing');

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await axios.post(`${API_BASE}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 120000 
      });
      
      if (response.data.status === 'completed') {
        setJobId(response.data.job_id);
        setStatus('completed');
      }
    } catch (error) {
      console.error("Upload failed:", error);
      setStatus('error');
    }
  };

  const handleTextSubmit = async () => {
    if (!rawText.trim()) return;
    setStatus('processing');

    try {
      const response = await axios.post(`${API_BASE}/upload`, { text: rawText }, {
        headers: { 'Content-Type': 'application/json' },
        timeout: 120000
      });
      
      if (response.data.status === 'completed') {
        setJobId(response.data.job_id);
        setStatus('completed');
      }
    } catch (error) {
      console.error("Text submission failed:", error);
      setStatus('error');
    }
  };

  const downloadFile = (type: 'full' | 'revision') => {
    if (!jobId) return;
    window.open(`${API_BASE}/download/${jobId}/${type}`, '_blank');
  };

  return (
    <main className="min-h-screen bg-[#0a0a0c] text-white selection:bg-purple-500/30">
      {/* Dynamic Background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-purple-600/20 blur-[120px] rounded-full" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-blue-600/10 blur-[120px] rounded-full" />
      </div>

      <nav className="relative z-10 flex items-center justify-between px-8 py-6 border-b border-white/5 backdrop-blur-md">
        <div className="flex items-center gap-2">
          <div className="p-2 bg-gradient-to-br from-purple-500 to-blue-600 rounded-lg">
            <BrainCircuit className="w-6 h-6" />
          </div>
          <span className="text-xl font-bold tracking-tight">AutoNotes <span className="text-purple-400">AI</span></span>
        </div>
      </nav>

      <section className="relative z-10 max-w-5xl mx-auto px-6 py-20 text-center">
        <motion.h1 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-5xl md:text-7xl font-extrabold mb-6 bg-clip-text text-transparent bg-gradient-to-b from-white to-gray-500"
        >
          Your raw thoughts, <br /> turned into <span className="text-purple-400">mastery.</span>
        </motion.h1>
        
        <div className="max-w-xl mx-auto">
          {status === 'idle' && (
            <div className="flex justify-center gap-4 mb-8">
              <button 
                onClick={() => setInputMode('upload')}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${inputMode === 'upload' ? 'bg-white text-black' : 'bg-white/5 text-gray-400 hover:bg-white/10'}`}
              >
                <Upload className="w-4 h-4 inline mr-2" /> Upload File
              </button>
              <button 
                onClick={() => setInputMode('text')}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${inputMode === 'text' ? 'bg-white text-black' : 'bg-white/5 text-gray-400 hover:bg-white/10'}`}
              >
                <Type className="w-4 h-4 inline mr-2" /> Paste Text
              </button>
            </div>
          )}

          <AnimatePresence mode="wait">
            {status === 'idle' && inputMode === 'upload' && (
              <motion.div
                key="upload"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="relative group"
              >
                <div className="absolute -inset-1 bg-gradient-to-r from-purple-600 to-blue-600 rounded-2xl blur opacity-25 group-hover:opacity-50 transition duration-1000 group-hover:duration-200"></div>
                <label className="relative flex flex-col items-center justify-center w-full h-64 border-2 border-dashed border-white/10 rounded-2xl bg-white/5 hover:bg-white/[0.07] transition-all cursor-pointer overflow-hidden backdrop-blur-xl">
                  <div className="flex flex-col items-center justify-center pt-5 pb-6">
                    <Upload className="w-12 h-12 text-gray-400 mb-4 group-hover:text-purple-400 transition-colors" />
                    <p className="mb-2 text-sm text-gray-400">
                      <span className="font-semibold">Click to upload</span> or drag and drop
                    </p>
                    <p className="text-xs text-gray-500">PDF or Text File</p>
                  </div>
                  <input type="file" className="hidden" onChange={handleUpload} />
                </label>
              </motion.div>
            )}

            {status === 'idle' && inputMode === 'text' && (
              <motion.div
                key="text"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="relative"
              >
                <textarea
                  value={rawText}
                  onChange={(e) => setRawText(e.target.value)}
                  placeholder="Paste your notes here..."
                  className="w-full h-64 p-6 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-xl text-white focus:border-purple-500/50 transition-colors resize-none"
                />
                <button 
                  onClick={handleTextSubmit}
                  className="absolute bottom-4 right-4 px-6 py-3 bg-purple-600 hover:bg-purple-500 rounded-xl font-bold flex items-center gap-2 transition-all shadow-xl shadow-purple-900/20"
                >
                  <Sparkles className="w-4 h-4" /> Generate Mastery
                </button>
              </motion.div>
            )}

            {status === 'processing' && (
              <motion.div
                key="processing"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="p-8 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-xl text-center"
              >
                <div className="flex justify-center mb-6">
                  <Loader2 className="w-12 h-12 text-purple-500 animate-spin" />
                </div>
                <h3 className="text-xl font-bold mb-2">Generating Notes...</h3>
                <p className="text-gray-400 text-sm">Please wait while the AI crafts your study materials.</p>
              </motion.div>
            )}

            {status === 'completed' && (
              <motion.div
                key="completed"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="grid grid-cols-1 md:grid-cols-2 gap-4 text-left"
              >
                <div className="p-6 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-xl">
                  <div className="flex items-center gap-3 mb-4">
                    <FileText className="w-5 h-5 text-purple-400" />
                    <h3 className="font-bold text-lg">Full Notes</h3>
                  </div>
                  <button 
                    onClick={() => downloadFile('full')}
                    className="w-full py-3 bg-purple-600 hover:bg-purple-500 rounded-xl font-semibold flex items-center justify-center gap-2 transition-all"
                  >
                    <Download className="w-4 h-4" /> Download .MD
                  </button>
                </div>

                <div className="p-6 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-xl">
                  <div className="flex items-center gap-3 mb-4">
                    <Zap className="w-5 h-5 text-blue-400" />
                    <h3 className="font-bold text-lg">Revision Sheet</h3>
                  </div>
                  <button 
                    onClick={() => downloadFile('revision')}
                    className="w-full py-3 bg-blue-600 hover:bg-blue-500 rounded-xl font-semibold flex items-center justify-center gap-2 transition-all"
                  >
                    <Download className="w-4 h-4" /> Download .MD
                  </button>
                </div>
                <button 
                  onClick={() => setStatus('idle')}
                  className="md:col-span-2 mt-4 text-gray-500 hover:text-white transition-colors text-sm"
                >
                  Start over
                </button>
              </motion.div>
            )}

            {status === 'error' && (
              <motion.div
                key="error"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="p-8 rounded-2xl bg-red-500/10 border border-red-500/20 backdrop-blur-xl text-center"
              >
                <h3 className="text-xl font-bold mb-2 text-red-400">Generation Failed</h3>
                <p className="text-gray-400 text-sm mb-6">The server didn't respond. Please check your internet or try again.</p>
                <button 
                  onClick={() => setStatus('idle')}
                  className="px-6 py-2 bg-white text-black rounded-full font-semibold"
                >
                  Try Again
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </section>

      <footer className="py-12 border-t border-white/5 text-center text-gray-500 text-sm">
        &copy; 2026 AutoNotes AI. All rights reserved.
      </footer>
    </main>
  );
}
