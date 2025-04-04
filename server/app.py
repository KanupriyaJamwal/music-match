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
# ===== NUCLEAR CORS SOLUTION =====
app.config['CORS_SUPPORTS_CREDENTIALS'] = True
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:3000",          # Development
            "https://kanupriyajamwal.github.io"  # Production
        ],
        "methods": ["GET", "POST", "OPTIONS", "PUT", "DELETE"],
        "allow_headers": ["*"],
        "expose_headers": ["*"],
        "supports_credentials": True,
        "max_age": 600
    }
})

# Temporary directory for processing
PROCESSING_DIR = os.path.join(tempfile.gettempdir(), 'spotify_wordcloud')
os.makedirs(PROCESSING_DIR, exist_ok=True)

@app.after_request
def inject_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response


# ===== API ENDPOINTS =====
@app.route('/api/data', methods=['GET', 'OPTIONS'])
def api_data():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    return jsonify({"status": "success", "data": "your_data"})

# Add a root route for health checks
@app.route('/')
def health_check():
    return jsonify({"status": "active", "message": "API is running"}), 200

@app.route('/generate_wordcloud', methods=['POST', 'OPTIONS'])  # Combined methods
def generate_wordcloud():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
        
    try:
        # Your existing POST logic here
        request_id = str(int(time.time()))
        work_dir = os.path.join(PROCESSING_DIR, request_id)
        os.makedirs(work_dir, exist_ok=True)
        
        script_path = os.path.join(work_dir, 'spotify_wordcloud.py')
        shutil.copyfile('spotify_wordcloud.py', script_path)
        
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            cwd=work_dir
        )
        
        if result.returncode != 0:
            return jsonify({'success': False, 'error': result.stderr}), 500
            
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
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/download/<request_id>/<filename>', methods=['GET'])
def download_file(request_id, filename):
    work_dir = os.path.join(PROCESSING_DIR, request_id)
    filepath = os.path.join(work_dir, filename)
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
        
    return send_file(filepath, as_attachment=True)

port = int(os.environ.get("PORT", 5001))  # Default to 5001 if PORT not set
if __name__ == '__main__':
    # Add host='0.0.0.0' to allow external connections
    app.run(host='0.0.0.0', port=5001, debug=True)