# AutoNotes AI

A premium, high-fidelity platform that turns unstructured material into mastery.

## Features
- **Multi-modal Ingestion:** Supports PDFs, Images (OCR), and Raw Text.
- **John (Full Notes):** Beginner-friendly, detailed study notes with examples.
- **Sally (Revision):** Rapid 10-minute revision sheets with memory tricks.
- **Glassmorphic UI:** Stunning modern dashboard built with Next.js and Framer Motion.

## ⚡ Power Options
You have three ways to run the AI engine:
1.  **Groq (Recommended):** Ultra-fast generation using `llama-3.3-70b-versatile`. Requires a [Groq API Key](https://console.groq.com/).
2.  **OpenAI:** High-quality results using `gpt-4o`. Requires an OpenAI Key.
3.  **Ollama (Free/Local):** Run for free on your own machine. Install [Ollama](https://ollama.com) and run `ollama run llama3`.

## Setup
1. Copy `.env.example` to `.env` and add your **GROQ_API_KEY** (or OpenAI key).
2. **Backend:**
   ```bash
   cd api
   pip install -r requirements.txt
   python main.py
   ```
3. **Frontend:**
   ```bash
   cd web
   npm install
   npm run dev
   ```

## Usage
- Open `http://localhost:3000`
- Upload your file and get your master-class notes in seconds.
