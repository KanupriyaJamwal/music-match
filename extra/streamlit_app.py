import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import lyricsgenius
import time
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import os
from collections import Counter
import re
import json
from pathlib import Path

# Configuration
SPOTIFY_CLIENT_ID="5ca4086451514b0696e84f251aa5541a" 
SPOTIFY_CLIENT_SECRET="6da4de03f49d4e0c988bfb36cbe46b76"
GENIUS_TOKEN = "N8YhKYgFQDuvrlDgw4FqvUIo2lWZ6XohnOqbG8rhunsrdQp7xJcyMmJLGq9SCW2S"
REDIRECT_URI = "http://localhost:8888/callback"

# UI Setup
st.set_page_config(
    page_title="Spotify Lyrics Word Cloud",
    page_icon="🎵",
    layout="wide"
)

# Custom CSS for better appearance
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6
    }
    .sidebar .sidebar-content {
        background: #ffffff
    }
    h1 {
        color: #1DB954;
    }
    .stProgress > div > div > div > div {
        background-color: #1DB954;
    }
</style>
""", unsafe_allow_html=True)

# Initialize APIs
@st.cache_resource
def init_spotify():
    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope="user-top-read",
        cache_path=".spotify_cache"
    ))

@st.cache_resource
def init_genius():
    return lyricsgenius.Genius(
        GENIUS_TOKEN,
        timeout=10,
        retries=2,
        verbose=False,
        remove_section_headers=True,
        skip_non_songs=True
    )

# Main App
def main():
    st.title("🎵 Spotify Lyrics Word Cloud Generator")
    st.markdown("Visualize your top songs' lyrics as a beautiful word cloud")
    
    with st.sidebar:
        st.header("Settings")
        time_range = st.selectbox(
            "Time Range",
            ["Last 4 weeks", "Last 6 months", "All time"],
            index=1
        )
        num_songs = st.slider("Number of Songs", 10, 50, 25)
        word_count = st.slider("Max Words in Cloud", 50, 500, 200)
        colormap = st.selectbox(
            "Color Theme",
            ["viridis", "plasma", "magma", "inferno", "cividis", "spring", "autumn"],
            index=0
        )
    
    # Convert UI selections to API parameters
    time_range_map = {
        "Last 4 weeks": "short_term",
        "Last 6 months": "medium_term",
        "All time": "long_term"
    }
    
    if st.button("Generate Word Cloud"):
        if not all([SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, GENIUS_TOKEN]):
            st.error("Please set all API credentials in the environment variables")
            return
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Get Spotify data
            status_text.text("Connecting to Spotify...")
            sp = init_spotify()
            progress_bar.progress(10)
            
            # Step 2: Fetch top tracks
            status_text.text(f"Fetching your top {num_songs} songs...")
            top_tracks = sp.current_user_top_tracks(
                limit=num_songs,
                time_range=time_range_map[time_range]
            )['items']
            progress_bar.progress(30)
            
            # Step 3: Prepare song data
            songs = [{
                'title': track['name'],
                'artist': ', '.join([a['name'] for a in track['artists']]),
                'album': track['album']['name']
            } for track in top_tracks]
            
            # Step 4: Fetch lyrics
            status_text.text("Fetching lyrics... (this may take a few minutes)")
            genius = init_genius()
            all_lyrics = ""
            
            for i, song in enumerate(songs):
                try:
                    result = genius.search_song(song['title'], song['artist'])
                    if result and result.lyrics:
                        all_lyrics += result.lyrics + "\n\n"
                except Exception as e:
                    st.warning(f"Couldn't fetch lyrics for {song['title']}: {str(e)}")
                
                progress_bar.progress(30 + int(50 * (i + 1) / len(songs)))
            
            # Step 5: Generate word cloud
            status_text.text("Generating word cloud...")
            
            # Process text
            def process_text(text):
                words = re.findall(r'\b[a-z]+\b', text.lower())
                return Counter(words)
            
            word_freq = process_text(all_lyrics)
            
            # Generate cloud
            wc = WordCloud(
                width=1200,
                height=800,
                background_color='white',
                colormap=colormap,
                max_words=word_count
            ).generate_from_frequencies(word_freq)
            
            # Display
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.imshow(wc, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)
            plt.close()
            
            # Show success
            progress_bar.progress(100)
            status_text.text("Done!")
            st.success("Your word cloud has been generated!")
            
            # Show song list
            with st.expander("Show Top Songs List"):
                for i, song in enumerate(songs, 1):
                    st.write(f"{i}. {song['title']} - {song['artist']}")
            
            # Download button
            st.download_button(
                label="Download Word Cloud",
                data=fig_to_bytes(fig),
                file_name="spotify_wordcloud.png",
                mime="image/png"
            )
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            progress_bar.progress(0)

def fig_to_bytes(fig):
    """Convert matplotlib figure to bytes for download"""
    import io
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=300)
    return buf.getvalue()

if __name__ == "__main__":
    main()