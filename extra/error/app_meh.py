
import shutil
from flask import Flask, flash, render_template, request, redirect, url_for, send_file, session
import os
from server.spotify_wordcloud import main as generate_wordcloud
import threading
import time
import matplotlib
matplotlib.use('Agg')  # Prevents GUI issues

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'
app.config['STATIC_FOLDER'] = 'static'

# Create directories if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
os.makedirs(app.config['STATIC_FOLDER'], exist_ok=True)

def run_generation(time_range, num_songs):
    """Thread target function to generate word cloud"""
    try:
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], 'lyrics_wordcloud.png')
        # Call the function with the expected arguments
        generate_wordcloud(time_range, num_songs, output_path)
    except Exception as e:
        app.logger.error(f"Generation error: {str(e)}")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        time_range = request.form.get('time_range', 'medium_term')
        num_songs = int(request.form.get('num_songs', 25))
        
        # Create thread with arguments
        thread = threading.Thread(
            target=run_generation,
            args=(time_range, num_songs)  # Pass as positional arguments
        )
        thread.start()
        
        return redirect(url_for('loading'))
    return render_template('index.html')

@app.route('/loading')
def loading():
    return render_template('loading.html')

@app.route('/results')
def results():
    #wordcloud_path = os.path.join(app.config['STATIC_FOLDER'], 'wordcloud.png')
    
    #if generation_status['in_progress']:
    #    flash("Generation still in progress", "info")
    #    return redirect(url_for('loading'))
    
    #if generation_status['error']:
    #    flash(f"Error: {generation_status['error']}", "error")
    #    return redirect(url_for('index'))
    
    #if not os.path.exists(wordcloud_path):
    #    flash("No word cloud found. Please generate one first.", "error")
    #    return redirect(url_for('index'))
    wordcloud_path = os.path.join(app.config['STATIC_FOLDER'], 'lyrics_wordcloud.png')
    if not os.path.exists(wordcloud_path):
        return redirect(url_for('loading'))
    
    return render_template('results.html')

@app.route('/download')
def download():
    output_path = os.path.join(app.config['STATIC_FOLDER'], 'lyrics_wordcloud.png')
    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)