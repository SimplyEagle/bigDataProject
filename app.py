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

# Last.fm API setup -TEMP Our model needs to replace this.
API_KEY = "e94245c03989b6fa22ae4cefb8de9dd0"
BASE_URL = "http://ws.audioscrobbler.com/2.0/"
HEADERS = {
    "User-Agent": "MusicRecommendationApp/1.0 (baileymsweeney@gmail.com)"
}

# Function to make Last.fm API requests -TEMP Our model needs to replace this.
def last_fm_request(method, params):
    params["api_key"] = API_KEY
    params["format"] = "json"
    url = BASE_URL + f"?method={method}"
    for key, value in params.items():
        url += f"&{key}={requests.utils.quote(value)}"
    print(f"Request URL: {url}")  # Debug statement
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API call failed: {e}")
        return None

# Functions for fetching similar artists, album info, and similar tracks
def get_similar_artists(artist):
    print(f"Fetching similar artists for: {artist}")
    result = last_fm_request("artist.getSimilar", {"artist": artist}) # TEMP - Model does work to find similar artists.
    print(f"Response Data: {result}")  # Print the full response for inspection
    return result

def get_album_info(artist, album):
    print(f"Fetching album info for: {album} by {artist}")
    result = last_fm_request("album.getInfo", {"artist": artist, "album": album}) # TEMP - Model does work to find similar album.
    print(f"Response Data: {result}")  # Print the full response for inspection
    return result

def get_similar_tracks(artist, track):
    print(f"Fetching similar tracks for: {track} by {artist}")
    result = last_fm_request("track.getSimilar", {"artist": artist, "track": track}) # TEMP - Model does work to find similar song.
    print(f"Response Data: {result}")  # Print the full response for inspection
    return result

# Function to get recommendations based on user input
def get_recommendations(user_input, data):
    recommendations = []
    user_input = user_input.lower()

    artist_matches = data['artists'][data['artists']['name'].str.lower().str.contains(user_input)]
    album_matches = data['albums'][data['albums']['name'].str.lower().str.contains(user_input)]
    song_matches = data['songs'][data['songs']['song_name'].str.lower().str.contains(user_input)]

    # Check for artist matches
    if not artist_matches.empty:
        artist = artist_matches.iloc[0]['name']
        result = get_similar_artists(artist)
        if result and 'similarartists' in result:
            recommendations += [artist["name"] for artist in result["similarartists"]["artist"]]

    # Check for album matches
    if not album_matches.empty:
        album = album_matches.iloc[0]
        artist_name = album['artists']
        result = get_album_info(artist_name, album['name'])
        if result and 'tracks' in result['album']:
            recommendations += [track["name"] for track in result["album"]["tracks"]["track"]]

    # Check for song matches
    if not song_matches.empty:
        song = song_matches.iloc[0]
        artist_name = song['artists']
        result = get_similar_tracks(artist_name, song['song_name'])
        if result and 'similartracks' in result:
            recommendations += [track["name"] for track in result["similartracks"]["track"]]

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
