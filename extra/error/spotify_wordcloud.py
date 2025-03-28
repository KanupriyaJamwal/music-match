import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import lyricsgenius
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import time
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re
from collections import Counter
import numpy as np
from PIL import Image

# Configuration
#SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
#SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_CLIENT_ID="5ca4086451514b0696e84f251aa5541a" 
SPOTIFY_CLIENT_SECRET="6da4de03f49d4e0c988bfb36cbe46b76"
GENIUS_TOKEN = "N8YhKYgFQDuvrlDgw4FqvUIo2lWZ6XohnOqbG8rhunsrdQp7xJcyMmJLGq9SCW2S"
REDIRECT_URI = "http://localhost:8888/callback"
CACHE_FILE = "lyrics_cache.json"
OUTPUT_FILE = "top_50_lyrics.txt"
WORDCLOUD_FILE = "lyrics_wordcloud.png"
MASK_FILE = None  # Optional: "mask_shape.png" for custom word cloud shapes

# Custom stopwords and processing
STOPWORDS = {
    'the', 'and', 'to', 'of', 'a', 'i', 'you', 'it', 'in', 'me', 'my',
    'that', 'is', 'be', 'with', 'for', 'on', 'not', 'this', 'are', 'your',
    'at', 'but', 'have', 'he', 'she', 'we', 'they', 'was', 'all', 'so'
}

# Initialize APIs with optimized settings
def init_apis():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope="user-top-read",
        cache_path=".spotify_cache",
        show_dialog=False  # Faster subsequent logins
    ))
    
    genius = lyricsgenius.Genius(
        GENIUS_TOKEN,
        timeout=8,               # Reduced timeout for faster failures
        retries=1,               # Fewer retries for speed
        verbose=False,
        remove_section_headers=True,
        skip_non_songs=True,
        excluded_terms=["Remix", "Live", "Version", "Edit"]
    )
    
    return sp, genius

# Caching system with expiration
class LyricsCache:
    def __init__(self):
        self.cache = {}
        self.load_cache()
    
    def load_cache(self):
        if Path(CACHE_FILE).exists():
            with open(CACHE_FILE, 'r') as f:
                self.cache = json.load(f)
    
    def save_cache(self):
        with open(CACHE_FILE, 'w') as f:
            json.dump(self.cache, f)
    
    def get(self, title, artist):
        key = f"{title.lower()}|{artist.lower()}"
        return self.cache.get(key)
    
    def set(self, title, artist, lyrics):
        key = f"{title.lower()}|{artist.lower()}"
        self.cache[key] = lyrics

# Fast lyrics fetching with parallel processing
def fetch_lyrics_parallel(songs, genius, cache):
    def fetch_single(song):
        cached = cache.get(song['title'], song['artist'])
        if cached:
            return song, cached
        
        try:
            result = genius.search_song(song['title'], song['artist'])
            lyrics = result.lyrics if result else None
            if lyrics:
                cache.set(song['title'], song['artist'], lyrics)
            return song, lyrics
        except Exception:
            return song, None
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fetch_single, song) for song in songs]
        results = []
        for future in as_completed(futures):
            results.append(future.result())
            time.sleep(0.1)  # Rate limiting
    
    return results

# Text processing for word cloud
def process_lyrics(text):
    # Remove metadata and special sections
    text = re.sub(r'\d+\. .*?\n', '', text)  # Remove song numbers
    text = re.sub(r'\[.*?\]', '', text)      # Remove section headers
    
    # Tokenize and clean
    words = re.findall(r"[a-z']+", text.lower())
    words = [w for w in words if w not in STOPWORDS and len(w) > 2]
    
    # Count frequencies
    return Counter(words)

# Generate optimized word cloud
def generate_wordcloud(word_freq):
    print("Generating word cloud...")
    
    # Optional mask for custom shapes
    mask = None
    if MASK_FILE and Path(MASK_FILE).exists():
        mask = np.array(Image.open(MASK_FILE))
    
    wc = WordCloud(
        width=1600,
        height=900,
        background_color='white',
        colormap='viridis',
        mask=mask,
        max_words=300,
        contour_width=1,
        contour_color='steelblue',
        collocations=False  # Better for lyrics
    ).generate_from_frequencies(word_freq)
    
    plt.figure(figsize=(16, 9))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(WORDCLOUD_FILE, dpi=300, bbox_inches='tight', pad_inches=0)
    plt.close()
    print(f"Word cloud saved to {WORDCLOUD_FILE}")

# Main workflow
def main():
    # Verify credentials
    if not all([SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET]):
        print("Error: Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET environment variables")
        return
    
    # Initialize
    sp, genius = init_apis()
    cache = LyricsCache()
    
    # Fetch top 50 songs
    print("Fetching your top 50 Spotify songs...")
    try:
        top_tracks = sp.current_user_top_tracks(limit=50, time_range='medium_term')['items']
        songs = [{
            'title': track['name'],
            'artist': ', '.join(a['name'] for a in track['artists'])
        } for track in top_tracks]
    except Exception as e:
        print(f"Spotify error: {e}")
        return
    
    # Fetch lyrics in parallel
    print(f"Fetching lyrics for {len(songs)} songs...")
    start_time = time.time()
    lyrics_results = fetch_lyrics_parallel(songs, genius, cache)
    cache.save_cache()
    
    # Save all lyrics to file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for song, lyrics in lyrics_results:
            f.write(f"{song['title']} - {song['artist']}\n")
            f.write(lyrics + "\n\n" if lyrics else " \n\n")
    
    # Generate word cloud from collected lyrics
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        word_freq = process_lyrics(f.read())
    
    generate_wordcloud(word_freq)
    
    print(f"\n✅ Completed in {time.time() - start_time:.1f} seconds")
    print(f"Lyrics saved to {OUTPUT_FILE}")
    print(f"Word cloud saved to {WORDCLOUD_FILE}")

if __name__ == "__main__":
    # Check for required packages
    try:
        import lyricsgenius, spotipy, spotify_wordcloud_old
    except ImportError:
        print("Installing required packages...")
        import subprocess
        subprocess.run(['pip', 'install', 'lyricsgenius', 'spotipy', 'wordcloud', 'matplotlib', 'pillow', 'numpy'])
    
    main()