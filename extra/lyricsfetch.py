import lyricsgenius
import time
from requests.exceptions import Timeout
import re
import os

# Initialize Genius with your token
GENIUS_TOKEN = os.getenv("GENIUS_TOKEN")
genius = lyricsgenius.Genius(
    GENIUS_TOKEN,
    timeout=15,
    retries=3,
    verbose=False,
    remove_section_headers=True  # Clean up lyrics
)

def parse_top_songs_file(filename="top_50_songs.txt"):
    """Parse our saved top 50 songs file"""
    songs = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip() and not line.startswith(('   ', 'Your', '===')):
                # Match lines like "1. Song Name - Artist"
                match = re.match(r'^\d+\. (.+?) - (.+)$', line.strip())
                if match:
                    songs.append({
                        'title': match.group(1).strip(),
                        'artist': match.group(2).strip()
                    })
    return songs

def get_lyrics(song_name, artist_name, max_retries=3):
    """Fetch lyrics with retries and error handling"""
    for attempt in range(max_retries):
        try:
            song = genius.search_song(title=song_name, artist=artist_name)
            if song:
                return song.lyrics
            return None
            
        except Timeout:
            if attempt < max_retries - 1:
                print(f"Timeout occurred, retrying ({attempt + 1}/{max_retries})...")
                time.sleep(2)
                continue
            return None
            
        except Exception as e:
            print(f"Error fetching {song_name}: {str(e)}")
            return None

def save_all_lyrics(songs, output_file="top_50_lyrics.txt"):
    """Fetch and save lyrics for all songs"""
    with open(output_file, 'w', encoding='utf-8') as f:
        for idx, song in enumerate(songs, 1):
            print(f"Fetching {idx}/50: {song['title']} by {song['artist']}...")
            
            lyrics = get_lyrics(song['title'], song['artist'])
            
            f.write(f"🎵 {song['title']} - {song['artist']} 🎵\n")
            f.write("="*50 + "\n")
            
            if lyrics:
                f.write(lyrics + "\n")
            else:
                f.write("Lyrics not found\n")
            
            f.write("\n\n")  # Add space between songs
            time.sleep(1)  # Be gentle with the API

if __name__ == "__main__":
    # Load the top 50 songs
    try:
        top_songs = parse_top_songs_file()
        if not top_songs:
            print("No songs found in top_50_songs.txt")
            print("Make sure to run the Spotify top songs fetcher first")
            exit(1)
            
        print(f"Found {len(top_songs)} songs in top_50_songs.txt")
        save_all_lyrics(top_songs)
        print("\n✅ All lyrics saved to top_50_lyrics.txt")
        
    except FileNotFoundError:
        print("Error: top_50_songs.txt not found")
        print("Please run the Spotify top songs fetcher first to generate this file")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")