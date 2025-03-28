import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Spotify API credentials
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8888/callback"  # Must match your Spotify app settings

def get_user_top_tracks(limit=50, time_range="medium_term"):
    """
    Fetch user's top tracks from Spotify
    
    Parameters:
    - limit: Number of tracks to fetch (max 50)
    - time_range: "short_term" (~4 weeks), "medium_term" (~6 months), "long_term" (several years)
    """
    # Set up authentication
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope="user-top-read",
        cache_path=".cache"  # Stores the token locally
    ))
    
    try:
        # Get top tracks
        results = sp.current_user_top_tracks(
            limit=limit,
            time_range=time_range
        )
        
        if not results['items']:
            print("No top tracks found. Have you listened to enough music?")
            return None
            
        return results['items']
        
    except Exception as e:
        print(f"Error fetching top tracks: {e}")
        return None

def display_top_tracks(tracks):
    """Display the top tracks in a formatted way"""
    print("\n🎵 Your Top 50 Songs on Spotify 🎵")
    print("----------------------------------")
    for idx, track in enumerate(tracks, 1):
        artists = ", ".join([artist['name'] for artist in track['artists']])
        print(f"{idx:2d}. {track['name']} - {artists}")
    #    print(f"    🔗 {track['external_urls']['spotify']}")
    #    print(f"    🎤 Album: {track['album']['name']}")
    #    print(f"    📅 Release Date: {track['album']['release_date']}")
        print()

def save_to_file(tracks, filename="top_50_songs.txt"):
    """Save the top tracks to a text file"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write("Your Top 50 Spotify Songs\n")
        f.write("=========================\n\n")
        for idx, track in enumerate(tracks, 1):
            artists = ", ".join([artist['name'] for artist in track['artists']])
            f.write(f"{idx}. {track['name']} - {artists}\n")
        #    f.write(f"   Album: {track['album']['name']}\n")
        #    f.write(f"   Release Date: {track['album']['release_date']}\n")
        #    f.write(f"   Spotify URL: {track['external_urls']['spotify']}\n\n")
    print(f"\n✅ Saved to {filename}")

if __name__ == "__main__":
    # Check if credentials are set
    if not CLIENT_ID or not CLIENT_SECRET:
        print("Error: Please set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in .env file")
        print("Get these from your Spotify Developer Dashboard")
        exit(1)
    
    print("Fetching your top 50 songs from Spotify...")
    
    # Get top tracks (medium_term = last 6 months)
    top_tracks = get_user_top_tracks(limit=50, time_range="medium_term")
    
    if top_tracks:
        display_top_tracks(top_tracks)
        save_to_file(top_tracks)
        
        print("\nTip: You can change the time range to:")
        print(" - 'short_term' (last 4 weeks)")
        print(" - 'long_term' (several years)")
        print("by modifying the time_range parameter in the code.")