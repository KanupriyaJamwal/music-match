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
CORS(app, resources={
    r"/services/*": {
        "origins": [
            "https://kanupriyajamwal.github.io",
            "http://localhost:3000"  # For development
        ]
    }
})
# Temporary directory for processing
PROCESSING_DIR = os.path.join(tempfile.gettempdir(), 'spotify_wordcloud')
os.makedirs(PROCESSING_DIR, exist_ok=True)


# Add a root route for health checks
@app.route('/')
def home():
    return jsonify({"status": "active", "message": "WordCloud Generator API"})

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
    app.run(port=port, debug=True)