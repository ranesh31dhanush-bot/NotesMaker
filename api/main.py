from flask import Flask, request, jsonify, send_file, make_response
from flask_cors import CORS
import uuid
import os
import logging
from processors.extractor import ContentExtractor
from generators.notes_pipeline import NotesGenerator
from dotenv import load_dotenv

# Initialize environment and logging
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Storage configuration (Render-compatible)
OUTPUT_DIR = "/tmp/autonotes_storage"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route("/", methods=["GET"])
def health():
    """Health check for Render deployment"""
    return jsonify({"status": "active", "service": "AutoNotes AI"}), 200

@app.route("/upload", methods=["POST", "OPTIONS"])
def upload_data():
    """Handle text and file uploads for note generation"""
    if request.method == "OPTIONS":
        return make_response("", 200)

    job_id = str(uuid.uuid4())
    
    try:
        # Extract input data
        if request.is_json:
            text = request.get_json().get('text', '')
        elif 'file' in request.files:
            file = request.files['file']
            text = ContentExtractor.extract(file.read(), file.content_type)
        else:
            text = request.form.get('text', '')

        if not text:
            return jsonify({"error": "No valid content provided"}), 400

        # Generate Notes
        logger.info(f"Processing job {job_id}...")
        full_notes = NotesGenerator.generate_full_notes(text)
        revision = NotesGenerator.generate_revision_notes(text)
        
        # Save to ephemeral storage
        full_path = os.path.join(OUTPUT_DIR, f"{job_id}_full.md")
        rev_path = os.path.join(OUTPUT_DIR, f"{job_id}_revision.md")
        
        with open(full_path, "w", encoding="utf-8") as f: f.write(full_notes)
        with open(rev_path, "w", encoding="utf-8") as f: f.write(revision)
        
        return jsonify({
            "job_id": job_id, 
            "status": "completed",
            "full_notes": full_notes,
            "revision": revision
        })

    except Exception as e:
        logger.error(f"Upload Error: {e}")
        return jsonify({"error": "An error occurred during generation. Please try again."}), 500

@app.route("/download/<job_id>/<type>")
def download_file(job_id, type):
    """Serve the generated markdown files"""
    path = os.path.join(OUTPUT_DIR, f"{job_id}_{type}.md")
    if os.path.exists(path):
        return send_file(path, as_attachment=True, download_name=f"AutoNotes_{type}.md")
    return jsonify({"error": "File expired or not found"}), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
