from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import uuid
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Use /tmp for storage (Standard for Render/Heroku)
OUTPUT_DIR = "/tmp/autonotes_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route("/", methods=["GET"])
def health():
    return "SERVER IS ALIVE", 200

@app.route("/ping", methods=["GET"])
def ping():
    return "pong", 200

@app.route("/upload", methods=["POST"])
def upload_data():
    # Lazy imports to prevent boot crashes
    from processors.extractor import ContentExtractor
    from generators.notes_pipeline import NotesGenerator
    
    logger.info("Upload request started")
    job_id = str(uuid.uuid4())
    
    try:
        if request.is_json:
            text = request.get_json().get('text', '')
        elif 'file' in request.files:
            file = request.files['file']
            text = ContentExtractor.extract(file.read(), file.content_type)
        else:
            text = request.form.get('text', '')

        if not text:
            return jsonify({"error": "No text"}), 400

        # Generate
        full_notes = NotesGenerator.generate_full_notes(text)
        revision = NotesGenerator.generate_revision_notes(text)
        
        # Save to /tmp
        full_path = os.path.join(OUTPUT_DIR, f"{job_id}_full.md")
        rev_path = os.path.join(OUTPUT_DIR, f"{job_id}_revision.md")
        
        with open(full_path, "w", encoding="utf-8") as f: f.write(full_notes)
        with open(rev_path, "w", encoding="utf-8") as f: f.write(revision)
        
        return jsonify({"job_id": job_id, "status": "completed"})

    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/download/<job_id>/<type>")
def download_file(job_id, type):
    path = os.path.join(OUTPUT_DIR, f"{job_id}_{type}.md")
    if os.path.exists(path):
        return send_file(path, as_attachment=True, download_name=f"notes_{type}.md")
    return "Not found", 404

if __name__ == "__main__":
    # Render sets the PORT environment variable
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
