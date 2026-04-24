from flask import Flask, request, jsonify, send_file, make_response
from flask_cors import CORS
from processors.extractor import ContentExtractor
from generators.notes_pipeline import NotesGenerator
from dotenv import load_dotenv
import uuid
import os
import logging

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- SMART ENV LOADING ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
env_files = ['.env', '.env.example', '.env.txt']
for folder in [current_dir, parent_dir]:
    for f_name in env_files:
        path = os.path.join(folder, f_name)
        if os.path.exists(path):
            load_dotenv(path)

app = Flask(__name__)

# --- RELAXED CORS FOR PRODUCTION ---
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Storage
OUTPUT_DIR = os.path.join(current_dir, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Store jobs
jobs = {}

@app.route("/", methods=["GET"])
def health():
    logger.info("Health check received")
    return jsonify({"status": "ready"}), 200

@app.route("/upload", methods=["POST", "OPTIONS"])
def upload_data():
    if request.method == "OPTIONS":
        return make_response("", 200)

    logger.info("--- Upload Request Started ---")
    job_id = str(uuid.uuid4())
    
    try:
        if request.is_json:
            text = request.get_json().get('text', '')
            logger.info("Received JSON text input")
        elif 'file' in request.files:
            file = request.files['file']
            text = ContentExtractor.extract(file.read(), file.content_type)
            logger.info(f"Received file: {file.filename}")
        elif 'text' in request.form:
            text = request.form['text']
            logger.info("Received form text input")
        else:
            logger.warning("No valid input in request")
            return jsonify({"error": "No input"}), 400

        if not text:
            logger.warning("Text extraction resulted in empty string")
            return jsonify({"error": "No text extracted"}), 400

        # Generate
        logger.info(f"Starting AI generation for Job: {job_id}")
        full_notes_md = NotesGenerator.generate_full_notes(text)
        revision_md = NotesGenerator.generate_revision_notes(text)
        
        # Save
        full_path = os.path.join(OUTPUT_DIR, f"{job_id}_full.md")
        rev_path = os.path.join(OUTPUT_DIR, f"{job_id}_revision.md")
        
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(full_notes_md)
        with open(rev_path, "w", encoding="utf-8") as f:
            f.write(revision_md)
        
        jobs[job_id] = {
            "status": "completed",
            "full_notes": full_notes_md,
            "revision": revision_md
        }
        
        logger.info(f"--- Job {job_id} Completed Successfully ---")
        return jsonify({"job_id": job_id, "status": "completed"})

    except Exception as e:
        logger.error(f"FATAL ERROR in /upload: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/status/<job_id>", methods=["GET"])
def get_status(job_id):
    return jsonify(jobs.get(job_id, {"status": "not_found"}))

@app.route("/download/<job_id>/<type>", methods=["GET"])
def download_file(job_id, type):
    filename = f"{job_id}_{type}.md"
    file_path = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True, download_name=f"AutoNotes_{type}.md")
    return jsonify({"error": "Not found"}), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
