from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import sys
import subprocess
import tempfile
import shutil
import time

app = Flask(__name__)

# Allow your GitHub Pages domain
# ======== CRITICAL CORS SETUP ========
app.config['CORS_HEADERS'] = 'Content-Type'

# ===== CRITICAL CORS SETUP =====
CORS(app, resources={
    r"/generate_wordcloud": {
        "origins": ["http://localhost:3000", "https://kanupriyajamwal.github.io"],
        "methods": ["POST", "OPTIONS"],  # Must include OPTIONS
        "allow_headers": ["Content-Type"]
    }
})

# Temporary directory for processing
PROCESSING_DIR = os.path.join(tempfile.gettempdir(), 'spotify_wordcloud')
os.makedirs(PROCESSING_DIR, exist_ok=True)

@app.after_request
def after_request(response):
    # Manually set headers as final fallback
    response.headers.add('Access-Control-Allow-Origin', 'https://kanupriyajamwal.github.io')
    response.headers.add('Access-Control-Allow-Headers', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

@app.route('/api/data', methods=['GET', 'OPTIONS'])
def api_data():
    if request.method == 'OPTIONS':
        return jsonify({"status": "preflight"}), 200  # Explicit OPTIONS response
    return jsonify({"data": "Successful CORS response"})

# Add a root route for health checks
@app.route('/')
def health_check():
    return jsonify({"status": "active", "message": "API is running"}), 200


# Explicit OPTIONS handler for preflight
@app.route('/generate_wordcloud', methods=['OPTIONS'])
def handle_preflight():
    return jsonify({"status": "preflight"}), 200

@app.route('/generate_wordcloud', methods=['POST'])
def generate_wordcloud():
    try:
        # Create a unique directory for this request
        request_id = str(int(time.time()))
        work_dir = os.path.join(PROCESSING_DIR, request_id)
        os.makedirs(work_dir, exist_ok=True)
        
        # Copy the script to the working directory
        script_path = os.path.join(work_dir, 'spotify_wordcloud.py')
        shutil.copyfile('spotify_wordcloud.py', script_path)
        
        # Run the Python script
        result = subprocess.run(
            [sys.executable, script_path],  # Use sys.executable instead of 'python'
            capture_output=True,
            text=True,
            cwd=work_dir
        )
        
        if result.returncode != 0:
            return jsonify({
                'success': False,
                'error': result.stderr
            }), 500
            
        # Check for output files
        output_files = {}
        for filename in ['top_50_lyrics.txt', 'lyrics_wordcloud.png']:
            filepath = os.path.join(work_dir, filename)
            if os.path.exists(filepath):
                output_files[filename] = f'/download/{request_id}/{filename}'
        
        return jsonify({
            'success': True,
            'output': result.stdout,
            'files': output_files
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/download/<request_id>/<filename>', methods=['GET'])
def download_file(request_id, filename):
    work_dir = os.path.join(PROCESSING_DIR, request_id)
    filepath = os.path.join(work_dir, filename)
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
        
    return send_file(filepath, as_attachment=True)

port = int(os.environ.get("PORT", 5000))  # Default to 5000 if PORT not set
if __name__ == '__main__':
    app.run(port=port)