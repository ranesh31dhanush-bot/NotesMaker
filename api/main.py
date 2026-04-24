from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from processors.extractor import ContentExtractor
from generators.notes_pipeline import NotesGenerator
from dotenv import load_dotenv
import uuid
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)
# Standard Flask-CORS setup (The most stable way)
CORS(app)

# Storage
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

jobs = {}

@app.route("/", methods=["GET"])
def health():
    logger.info("Health check received")
    return jsonify({"status": "ready", "msg": "AutoNotes Backend is Live"}), 200

@app.route("/ping", methods=["GET"])
def ping():
    return "pong", 200

@app.route("/upload", methods=["POST"])
def upload_data():
    logger.info(">>> [POST] /upload request started")
    job_id = str(uuid.uuid4())
    
    try:
        # 1. Extraction logic
        if request.is_json:
            text = request.get_json().get('text', '')
        elif 'file' in request.files:
            file = request.files['file']
            text = ContentExtractor.extract(file.read(), file.content_type)
        else:
            text = request.form.get('text', '')

        if not text:
            logger.warning("No text found in request payload")
            return jsonify({"error": "No text detected"}), 400

        logger.info(f"Processing {len(text)} characters of text...")
        
        # 2. GENERATE (Synchronous)
        full_notes = NotesGenerator.generate_full_notes(text)
        revision = NotesGenerator.generate_revision_notes(text)
        
        # 3. SAVE TO DISK
        full_path = os.path.join(OUTPUT_DIR, f"{job_id}_full.md")
        rev_path = os.path.join(OUTPUT_DIR, f"{job_id}_revision.md")
        
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(f"# Study Notes\n\n{full_notes}")
        with open(rev_path, "w", encoding="utf-8") as f:
            f.write(f"# Revision Sheet\n\n{revision}")
        
        jobs[job_id] = {"status": "completed"}
        
        logger.info(f">>> [SUCCESS] Job {job_id} completed")
        return jsonify({
            "job_id": job_id, 
            "status": "completed",
            "full_notes": full_notes,
            "revision": revision
        })

    except Exception as e:
        logger.error(f"!!! [ERROR] In /upload: {str(e)}")
        return jsonify({"error": "An internal error occurred while generating notes."}), 500

@app.route("/download/<job_id>/<type>")
def download_file(job_id, type):
    path = os.path.join(OUTPUT_DIR, f"{job_id}_{type}.md")
    if os.path.exists(path):
        return send_file(path, as_attachment=True, download_name=f"AutoNotes_{type}.md")
    return "File not found", 404

if __name__ == "__main__":
    # Fallback for local testing
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
