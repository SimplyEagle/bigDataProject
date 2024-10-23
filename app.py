import streamlit as st
import requests
import pandas as pd

# Function to load a single CSV file
def load_single_file(file_path):
    return pd.read_csv(file_path, delimiter='\t')

# Function to load data
@st.cache_data
def load_data(file_paths):
    data_frames = {key: load_single_file(path) for key, path in file_paths.items()}
    return data_frames

# Last.fm API setup
API_KEY = "ab78ee3e9138734685369ef76a64bb90"
BASE_URL = "http://ws.audioscrobbler.com/2.0/"
HEADERS = {
    "User-Agent": "MusicRecommendationApp/1.0 (baileymsweeney@gmail.com)"
}

# Function to make Last.fm API requests
def last_fm_request(method, params):
    try:
        response = requests.get(BASE_URL, headers=HEADERS, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API call failed: {e}")
        print(f"Failed request with params: {params}")  # Print the parameters that failed
        return None

# Functions for fetching similar artists, album info, and similar tracks
def get_similar_artists(artist):
    print(f"Fetching similar artists for: {artist}")
    params = {"artist": artist, "api_key": API_KEY, "format": "json"}
    return last_fm_request("artist.getSimilar", params)

def get_album_info(artist, album):
    artist_name = artist['artist_name']  # Extract just the name from the dictionary
    print(f"Fetching album info for: {album} by {artist_name}")
    params = {"artist": artist_name, "album": album, "api_key": API_KEY, "format": "json"}
    return last_fm_request("album.getInfo", params)

def get_similar_tracks(artist, track):
    print(f"Fetching similar tracks for: {track} by {artist}")
    params = {"artist": artist, "track": track, "api_key": API_KEY, "format": "json"}
    return last_fm_request("track.getSimilar", params)

# Function to get recommendations based on user input
def get_recommendations(user_input, data):
    recommendations = []
    user_input = user_input.lower()

    # Search through the loaded data
    artist_matches = data['artists'][data['artists']['name'].str.lower().str.contains(user_input)]
    album_matches = data['albums'][data['albums']['name'].str.lower().str.contains(user_input)]
    song_matches = data['songs'][data['songs']['song_name'].str.lower().str.contains(user_input)]

    # Check for artist matches
    if not artist_matches.empty:
        artist = artist_matches.iloc[0]['name']  # Get the first matching artist
        recommendations += get_similar_artists(artist) or []

    # Check for album matches
    if not album_matches.empty:
        album = album_matches.iloc[0]  # Get the first matching album
        recommendations += get_album_info(album['artists'], album['name']) or []

    # Check for song matches
    if not song_matches.empty:
        song = song_matches.iloc[0]  # Get the first matching song
        recommendations += get_similar_tracks(song['artists'], song['song_name']) or []

    return recommendations

# Streamlit UI
st.title("Real-Time Music Recommendations")
st.write("Enter an artist, album, or song to get recommendations.")

user_input = st.text_input("What music are you interested in?")

# Load all data files at the start
file_paths = {
    "albums": 'musicoset_metadata/albums.csv',
    "artists": 'musicoset_metadata/artists.csv',
    "songs": 'musicoset_metadata/songs.csv',
    "tracks": 'musicoset_metadata/tracks.csv',
}
data = load_data(file_paths)

if st.button("Get Recommendations"):
    if user_input:
        recommendations = get_recommendations(user_input, data)

        if recommendations:
            st.write("Here are your recommendations:")
            for rec in recommendations:
                st.write(f"- {rec}")
        else:
            st.write("No recommendations found. Try another input.")
    else:
        st.write("Please enter some input.")
