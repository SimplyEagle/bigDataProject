import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors


# Load both datasets
def load_data(file_paths):
    try:
        # Load songs and features CSVs
        songs = pd.read_csv(file_paths["songs"], on_bad_lines='warn', delimiter='\t')
        features = pd.read_csv(file_paths["acoustic_features"], on_bad_lines='warn', delimiter='\t')

        print("Songs DataFrame:", songs.head())  # Debugging step
        print("Features DataFrame:", features.head())  # Debugging step

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
    knn = NearestNeighbors(n_neighbors=5, metric='euclidean')
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

    # Return recommended songs
    recommendations = songs_df.iloc[indices[0]]
    return recommendations["song_name"].tolist()


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

        print("Here are your recommendations:")
        for rec in recommendations:
            print(rec)
