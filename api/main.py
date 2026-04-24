from flask import Flask, request, jsonify, send_file, make_response
from flask_cors import CORS
from processors.extractor import ContentExtractor
from generators.notes_pipeline import NotesGenerator
from dotenv import load_dotenv
import uuid
import os
import logging

# Set up logging to be very visible
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)
CORS(app) # Broadest possible CORS

# Storage
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

jobs = {}

@app.route("/", methods=["GET"])
def health():
    return "OK", 200

@app.route("/upload", methods=["POST", "OPTIONS"])
def upload_data():
    if request.method == "OPTIONS":
        return make_response("", 200)

    logger.info(">>> UPLOAD REQUEST RECEIVED <<<")
    job_id = str(uuid.uuid4())
    
    try:
        # Get input
        if request.is_json:
            text = request.get_json().get('text', '')
        elif 'file' in request.files:
            file = request.files['file']
            text = ContentExtractor.extract(file.read(), file.content_type)
        else:
            text = request.form.get('text', '')

        if not text:
            logger.error("No text found in request")
            return jsonify({"error": "No text"}), 400

        logger.info(f"Generating notes for {len(text)} chars of text...")
        
        # GENERATE (Synchronous)
        full_notes = NotesGenerator.generate_full_notes(text)
        revision = NotesGenerator.generate_revision_notes(text)
        
        # SAVE
        full_path = os.path.join(OUTPUT_DIR, f"{job_id}_full.md")
        rev_path = os.path.join(OUTPUT_DIR, f"{job_id}_revision.md")
        
        with open(full_path, "w", encoding="utf-8") as f: f.write(full_notes)
        with open(rev_path, "w", encoding="utf-8") as f: f.write(revision)
        
        jobs[job_id] = {"status": "completed"}
        
        logger.info(">>> UPLOAD COMPLETED <<<")
        return jsonify({"job_id": job_id, "status": "completed"})

    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/status/<job_id>")
def get_status(job_id):
    return jsonify(jobs.get(job_id, {"status": "not_found"}))

@app.route("/download/<job_id>/<type>")
def download_file(job_id, type):
    path = os.path.join(OUTPUT_DIR, f"{job_id}_{type}.md")
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "Not found", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
