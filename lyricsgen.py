import lyricsgenius
import argparse
import os
import time
from requests.exceptions import Timeout

def get_lyrics(song_name, artist_name, max_retries=3):
    genius_token = os.getenv("GENIUS_API_TOKEN")
    if not genius_token:
        raise ValueError("Missing GENIUS_API_TOKEN environment variable")

#export GENIUS_API_TOKEN="your-api-token-here"  # Linux/Mac
# or 
#set GENIUS_API_TOKEN="your-api-token-here"  # Windows CMD
# get genius client access id from notion but its also this - N8YhKYgFQDuvrlDgw4FqvUIo2lWZ6XohnOqbG8rhunsrdQp7xJcyMmJLGq9SCW2S

    # Initialize client with longer timeout
    genius = lyricsgenius.Genius(
        genius_token,
        timeout=15,  # Increase timeout to 15 seconds
        retries=3,   # Number of retries for failed requests
        verbose=False
    )
    
    for attempt in range(max_retries):
        try:
            song = genius.search_song(title=song_name, artist=artist_name)
            if song:
                return song.lyrics
            return "Lyrics not found"
            
        except Timeout:
            if attempt < max_retries - 1:
                print(f"Timeout occurred, retrying ({attempt + 1}/{max_retries})...")
                time.sleep(2)  # Wait before retrying
                continue
            return "Error: Request timed out after multiple attempts"
            
        except Exception as e:
            return f"Error occurred: {str(e)}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get song lyrics')
    parser.add_argument('--song', required=True, help='Song title')
    parser.add_argument('--artist', required=True, help='Artist name')
    
    args = parser.parse_args()
    
    lyrics = get_lyrics(args.song, args.artist)
    print(lyrics)