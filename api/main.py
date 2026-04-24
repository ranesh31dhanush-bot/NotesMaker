from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from processors.extractor import ContentExtractor
from generators.notes_pipeline import NotesGenerator
from dotenv import load_dotenv
import uuid
import os
import threading

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

# --- PRODUCTION CORS ---
# This allows your Vercel frontend to talk to this Render backend
CORS(app, resources={r"/*": {"origins": "*"}})

# Storage
OUTPUT_DIR = os.path.join(current_dir, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# In-memory job store
jobs = {}

# --- HEALTH CHECK ROUTE (CRITICAL FOR RENDER) ---
@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "service": "AutoNotes AI API"}), 200

@app.route("/upload", methods=["POST"])
def upload_data():
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "processing", "full_notes": None, "revision": None}
    
    if request.is_json:
        data = request.get_json()
        raw_text = data.get('text', '')
        thread = threading.Thread(target=process_job, args=(job_id, raw_text, "text/plain", True))
    elif 'file' in request.files:
        file = request.files['file']
        content_bytes = file.read()
        content_type = file.content_type
        thread = threading.Thread(target=process_job, args=(job_id, content_bytes, content_type, False))
    elif 'text' in request.form:
        raw_text = request.form['text']
        thread = threading.Thread(target=process_job, args=(job_id, raw_text, "text/plain", True))
    else:
        return jsonify({"error": "No valid input detected."}), 400
    
    thread.start()
    return jsonify({"job_id": job_id})

@app.route("/status/<job_id>", methods=["GET"])
def get_status(job_id):
    return jsonify(jobs.get(job_id, {"status": "not_found"}))

@app.route("/download/<job_id>/<type>", methods=["GET"])
def download_file(job_id, type):
    if job_id not in jobs or jobs[job_id]["status"] != "completed":
        return jsonify({"error": "File not ready"}), 404
    
    filename = f"{job_id}_{type}.md"
    file_path = os.path.join(OUTPUT_DIR, filename)
    
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True, download_name=f"AutoNotes_{type}.md")
    return jsonify({"error": "File not found"}), 404

def process_job(job_id, input_data, content_type, is_raw_text):
    try:
        # 1. Extract
        if is_raw_text:
            text = input_data
        else:
            text = ContentExtractor.extract(input_data, content_type)
        
        if not text:
            raise ValueError("Empty input.")

        # 2. Generate
        full_notes_md = NotesGenerator.generate_full_notes(text)
        revision_md = NotesGenerator.generate_revision_notes(text)
        
        # 3. Save
        full_path = os.path.join(OUTPUT_DIR, f"{job_id}_full.md")
        rev_path = os.path.join(OUTPUT_DIR, f"{job_id}_revision.md")
        
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(f"# Full Study Notes\n\n{full_notes_md}")
            
        with open(rev_path, "w", encoding="utf-8") as f:
            f.write(f"# Rapid Revision Sheet\n\n{revision_md}")
        
        # 4. Finalize
        jobs[job_id] = {
            "status": "completed",
            "full_notes": full_notes_md,
            "revision": revision_md
        }
    except Exception as e:
        print(f"Error: {e}")
        jobs[job_id] = {"status": "failed", "error": str(e)}

if __name__ == "__main__":
    # Use the PORT provided by Render, or default to 8000
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=False)
