import pandas as pd
import requests
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors

# Define Last.fm API credentials and base URL
API_KEY = "2a3003eeec5dd58eb2ee4540e93b7267"
BASE_URL = "https://ws.audioscrobbler.com/2.0/"

# Load both datasets
def load_data(file_paths):
    try:
        # Load songs and features CSVs
        songs = pd.read_csv(file_paths["songs"], on_bad_lines='warn', delimiter='\t')
        features = pd.read_csv(file_paths["acoustic_features"], on_bad_lines='warn', delimiter='\t')

        # Parse artist dictionary column in songs.csv
        songs[["artist_id", "artist_name"]] = pd.DataFrame(
            [list(entry.items())[0] for entry in songs["artists"].apply(eval)],
            index=songs.index
        )

        # Merge songs with acoustic features on song ID or relevant key
        merged_data = pd.merge(songs, features, on="song_id", how="inner")

        return {"songs": merged_data}

    except Exception as e:
        print(f"Error loading data: {e}")
        return {}  # Return an empty dictionary in case of an error


# Train KNN model
def train_knn_model(songs_df):
    # Define relevant feature columns
    feature_columns = [
        'danceability', 'energy', 'loudness', 'speechiness',
        'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo'
    ]

    # Ensure only existing columns are selected
    existing_columns = [col for col in feature_columns if col in songs_df.columns]
    if not existing_columns:
        raise ValueError("No matching feature columns found in the dataset.")

    # Scale the features
    scaler = StandardScaler()
    X = scaler.fit_transform(songs_df[existing_columns])

    # Train the KNN model
    knn = NearestNeighbors(n_neighbors=10, metric='euclidean')  # Increase neighbors to 10
    knn.fit(X)

    return knn, scaler


# Get song recommendations using KNN
def get_recommendations(song_name, songs_df, knn_model, scaler):
    feature_columns = [
        'danceability', 'energy', 'loudness', 'speechiness',
        'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo'
    ]

    # Find the matching song's features
    song = songs_df[songs_df["song_name"].str.contains(song_name, case=False, na=False)]
    if song.empty:
        print(f"No song found with name: {song_name}")
        return []

    # Extract and scale the features of the input song
    song_features = song[feature_columns]
    scaled_features = scaler.transform(song_features)

    # Find the nearest neighbors
    distances, indices = knn_model.kneighbors(scaled_features)

    # Prepare recommendations and their statistics
    recommendations = songs_df.iloc[indices[0]]
    recommendation_stats = []
    for i, idx in enumerate(indices[0]):
        song_info = recommendations.iloc[i]
        stats = {
            "song_name": song_info["song_name"],
            "artist_name": song_info["artist_name"],
            "distance": distances[0][i],
            "features": {col: song_info[col] for col in feature_columns},
        }
        recommendation_stats.append(stats)

    # Return only the first 6 recommendations with the input song as the first
    return recommendation_stats[:6]


# Function to get similar songs using Last.fm API
def get_similar_songs_from_api(song_name, artist_name=None):
    try:
        params = {
            "method": "track.getsimilar",
            "track": song_name,
            "api_key": API_KEY,
            "format": "json",
        }
        if artist_name:
            params["artist"] = artist_name

        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if "similartracks" in data and "track" in data["similartracks"]:
            similar_tracks = data["similartracks"]["track"]

            # Extract relevant details and sort by match (descending for better match)
            tracks_sorted = sorted(
                [
                    {
                        "song_name": track["name"],
                        "artist_name": track["artist"]["name"],
                        "match": float(track.get("match", 0)),  # Match score if available
                    }
                    for track in similar_tracks
                ],
                key=lambda x: x["match"],
                reverse=True  # Descending order
            )

            # Return top 10 results
            return tracks_sorted[:10]
        else:
            print(f"No similar songs found for '{song_name}'.")
            return []
    except Exception as e:
        print(f"Error fetching similar songs from Last.fm: {e}")
        return []


# Main Program
if __name__ == "__main__":
    # File paths to the datasets
    file_paths = {
        "songs": "musicoset_metadata/songs.csv",
        "acoustic_features": "musicoset_songfeatures/acoustic_features.csv"
    }

    # Load data
    data = load_data(file_paths)

    # Check if data was loaded successfully
    if not data:
        print("Failed to load data. Exiting program.")
    else:
        # Train the KNN model
        knn_model, scaler = train_knn_model(data["songs"])

        # Get user input and recommend songs
        user_input = input("Enter a song name to get recommendations: ")
        recommendations = get_recommendations(user_input, data["songs"], knn_model, scaler)

        # Get similar songs from Last.fm for all KNN results (skip the first recommendation if it matches)
        all_similar_songs = []
        first_song_name = recommendations[0]["song_name"]  # First recommendation song name
        for rec in recommendations[1:]:  # Skip the first recommendation
            similar_songs = get_similar_songs_from_api(
                song_name=rec["song_name"],
                artist_name=rec["artist_name"]
            )

            # Filter out similar songs that match the first recommendation's song name
            filtered_songs = [song for song in similar_songs if song["song_name"].lower() != first_song_name.lower()]
            all_similar_songs.extend(filtered_songs)

        # Compile the match scores for each song
        song_match_scores = {}
        for song in all_similar_songs:
            song_name = song["song_name"]
            artist_name = song["artist_name"]  # Ensure we capture the artist as well
            match_score = song["match"]

            if song_name not in song_match_scores:
                song_match_scores[song_name] = {
                    "artist_name": artist_name,  # Add artist name to the match score data
                    "total_match_score": 0  # Initialize match score if new song
                }
            song_match_scores[song_name]["total_match_score"] += match_score  # Add the match score

        # Sort by total match score (descending)
        sorted_similar_songs = sorted(
            [{"song_name": song_name, "artist_name": data["artist_name"], "total_match_score": data["total_match_score"]}
             for song_name, data in song_match_scores.items()],
            key=lambda x: x["total_match_score"],
            reverse=True
        )
        # Add match score to content-based recommendations and print
        print("\nContent-Based Recommendations with Hybrid Match Scores:")
        for rec in recommendations[1:]:
            hybrid_match_score = 0  # Default match score
            for hybrid_song in sorted_similar_songs:
                if hybrid_song["song_name"].lower() == rec["song_name"].lower():
                    hybrid_match_score = hybrid_song["total_match_score"]
                    break
            print(f"Song: {rec['song_name']}, Artist: {rec['artist_name']}, Distance: {rec['distance']:.4f}, Match Score: {hybrid_match_score:.5f}")

        # Output the top 5 most similar songs with total match scores
        print("\nTop 5 Most Similar Songs (Hybrid Recommendations):")
        for song in sorted_similar_songs[:5]:
            print(f"Song: {song['song_name']}, Artist: {song['artist_name']}, Total Match Score: {song['total_match_score']:.5f}")
