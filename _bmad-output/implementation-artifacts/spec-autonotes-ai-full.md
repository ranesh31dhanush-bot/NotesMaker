---
title: 'AutoNotes AI Full Stack Implementation'
type: 'feature'
created: '2026-04-24T11:21:00Z'
status: 'draft'
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Students and professionals often have high volumes of unstructured study material (chats, PDFs, images) but lack the time to manually structure them into effective study notes and quick revision sheets.

**Approach:** Build "AutoNotes AI," a full-stack platform that ingests unstructured data via a Next.js dashboard, processes it through a FastAPI-based async pipeline (extraction, cleaning, generation, and PDF formatting), and delivers high-fidelity "Full Notes" and "Revision Sheets" to the user.

## Boundaries & Constraints

**Always:** Use the "Persona-based" prompt strategy (John for notes, Sally for revisions). Ensure high-fidelity aesthetics (glassmorphism, modern typography) in the UI.

**Ask First:** If any file exceeds 100MB or if OCR processing takes more than 2 minutes.

**Never:** Store raw user text permanently after 24 hours (privacy first). Do not use generic browser default styles.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Happy Path | PDF Upload | Two downloadable PDFs: `full_notes.pdf` and `revision.pdf` | N/A |
| Image Upload | PNG/JPG with text | OCR extraction follows by note generation | Alert if OCR fails to find text |
| Large Input | 50+ pages text | Content chunked and processed in stages | Notify user of "Processing Large Document" |

</frozen-after-approval>

## Code Map

- `web/` -- Next.js 14 (App Router) Frontend
- `api/` -- FastAPI (Python 3.11+) Backend
- `web/src/app/page.tsx` -- Main Dashboard UI
- `api/main.py` -- API Entry point & Job Orchestrator
- `api/processors/extractor.py` -- PDF & OCR extraction logic
- `api/generators/notes_pipeline.py` -- LLM orchestration (Claude/GPT)
- `api/utils/pdf_engine.py` -- Puppeteer-based PDF generation

## Tasks & Acceptance

**Execution:**
- [ ] `web/` -- Initialize Next.js project with Tailwind and Supabase -- Setup frontend foundation.
- [ ] `api/` -- Initialize FastAPI project with requirements -- Setup backend foundation.
- [ ] `api/processors/extractor.py` -- Implement PDF (pdfplumber) and OCR (pytesseract) logic -- Support multi-modal inputs.
- [ ] `api/generators/notes_pipeline.py` -- Implement John (Full Notes) and Sally (Revision) prompts -- Core AI logic.
- [ ] `api/utils/pdf_engine.py` -- Implement Puppeteer HTML-to-PDF rendering -- Professional output formatting.
- [ ] `web/src/components/UploadDashboard.tsx` -- Build the glassmorphic upload and status UI -- Premium user experience.

**Acceptance Criteria:**
- Given a PDF upload, when the process completes, then the user can download a well-structured `full_notes.pdf` and a concise `revision.pdf`.
- Given an image with text, when uploaded, then the system extracts the text via OCR and proceeds with generation.
- Given the Dashboard, when viewed, then it displays a premium, modern aesthetic with real-time status updates from the backend.

## Design Notes

**Prompt Strategy:** 
- **John (PM):** "Act as a professional teacher. Create detailed notes with headings, examples, and simple explanations."
- **Sally (UX):** "Act as a memory expert. Compress content into a 10-minute revision sheet using keywords and memory tricks."

## Verification

**Commands:**
- `npm run dev` -- expected: Next.js frontend running locally.
- `uvicorn main:app --reload` -- expected: FastAPI backend running locally.

**Manual checks (if no CLI):**
- Inspect the generated PDFs for layout consistency, page numbers, and table of contents.
