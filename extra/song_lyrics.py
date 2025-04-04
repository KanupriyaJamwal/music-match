import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import lyricsgenius
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import time
import re

# Configuration
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
GENIUS_TOKEN = os.getenv("GENIUS_TOKEN")
REDIRECT_URI = "http://localhost:8888/callback"
CACHE_FILE = "lyrics_cache.json"
OUTPUT_FILE = "top_50_with_lyrics.txt"

# Initialize APIs
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope="user-top-read",
    cache_path=".spotify_cache"
))

genius = lyricsgenius.Genius(
    GENIUS_TOKEN,
    timeout=10,
    retries=2,
    verbose=False,
    remove_section_headers=True,
    skip_non_songs=True,
    excluded_terms=["(Remix)", "(Live)", "(Demo)"]
)

# Caching system
def load_cache():
    if Path(CACHE_FILE).exists():
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

def get_cached_lyrics(title, artist, cache):
    key = f"{title.lower()}|{artist.lower()}"
    return cache.get(key)

# Lyrics fetching with parallel processing
def fetch_lyrics_batch(songs):
    cache = load_cache()
    results = []
    uncached_songs = []
    
    # Check cache first
    for song in songs:
        cached = get_cached_lyrics(song['title'], song['artist'], cache)
        if cached:
            results.append((song, cached))
        else:
            uncached_songs.append(song)
    
    # Process uncached songs in parallel
    if uncached_songs:
        with ThreadPoolExecutor(max_workers=8) as executor:
            future_to_song = {
                executor.submit(
                    genius.search_song, 
                    title=song['title'], 
                    artist=song['artist']
                ): song 
                for song in uncached_songs
            }
            
            for future in future_to_song:
                song = future_to_song[future]
                try:
                    result = future.result()
                    lyrics = result.lyrics if result else "Lyrics not found"
                    results.append((song, lyrics))
                    cache[f"{song['title'].lower()}|{song['artist'].lower()}"] = lyrics
                except Exception as e:
                    results.append((song, f"Error: {str(e)}"))
                    continue
        
        save_cache(cache)
    
    return sorted(results, key=lambda x: songs.index(x[0]))

# Main function
def get_top_50_with_lyrics():
    # Get top 50 tracks from Spotify
    print("Fetching your top 50 songs from Spotify...")
    top_tracks = sp.current_user_top_tracks(limit=50, time_range="medium_term")['items']
    
    if not top_tracks:
        print("No top tracks found. Have you listened to enough music?")
        return
    
    # Prepare song data
    songs = [{
        'title': track['name'],
        'artist': ', '.join([a['name'] for a in track['artists']]),
        'album': track['album']['name'],
        'url': track['external_urls']['spotify']
    } for track in top_tracks]
    
    # Fetch lyrics in parallel with caching
    print("Fetching lyrics (this may take a minute)...")
    start_time = time.time()
    songs_with_lyrics = fetch_lyrics_batch(songs)
    elapsed = time.time() - start_time
    
    # Save results
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("🎵 Your Top 50 Spotify Songs with Lyrics 🎵\n")
        f.write("="*60 + "\n\n")
        
        for idx, (song, lyrics) in enumerate(songs_with_lyrics, 1):
            f.write(f"{idx}. {song['title']} - {song['artist']}\n")
            f.write(f"   Album: {song['album']}\n")
            f.write(f"   Spotify: {song['url']}\n")
            f.write("-"*50 + "\n")
            f.write(lyrics + "\n")
            f.write("\n" + "="*50 + "\n\n")
    
    print(f"✅ Done! Saved to {OUTPUT_FILE}")
    print(f"Fetched {len(songs_with_lyrics)} songs in {elapsed:.1f} seconds")

if __name__ == "__main__":
    if not all([SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET]):
        print("Error: Please set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET environment variables")
        exit(1)
    
    try:
        get_top_50_with_lyrics()
    except Exception as e:
        print(f"An error occurred: {e}")