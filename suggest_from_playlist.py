import collections
import spotipy

pitch_names = ['C', 'C#/Db', 'D', 'D#/Eb', 'E', 'F', 'F#/Gb', 'G', 'G#/Ab', 'A', 'A#/Bb', 'B']

def generate_playlist_tracks(access_token, playlist_id, limit=50):
    spotify = spotipy.Spotify(auth=access_token)
    
    # Retrieve the tracks from the selected playlist
    playlist_tracks = spotify.playlist_tracks(playlist_id)
    playlist_track_ids = set(track['track']['id'] for track in playlist_tracks['items'])

    # Get the artist IDs from the playlist tracks
    artist_ids = [track['track']['artists'][0]['id'] for track in playlist_tracks['items']]

    # Get information about all artists in the playlist
    artists_info = []
    for i in range(0, len(artist_ids), 50):
        batch = artist_ids[i:i+50]
        artists_info.extend(spotify.artists(batch)['artists'])

    # Get the genres of the artists
    artist_genres = [artist['genres'] for artist in artists_info]

    # Find the most common genres
    flattened_genres = [genre for genres in artist_genres for genre in genres]
    most_common_genre = collections.Counter(flattened_genres).most_common(1)[0][0] 

    # Use the playlist tracks as seeds for song recommendations
    seeded_tracks = list(playlist_track_ids)[:4]

    # Retrieve song recommendations based on track and genre seeds
    song_recommendations = spotify.recommendations(seed_tracks=seeded_tracks, seed_genres=[most_common_genre], limit=limit)

    # Prepare the data for output
    track_data = []
    recommended_track_ids = [track['id'] for track in song_recommendations['tracks'] if track['id'] not in playlist_track_ids]
    track_audio_features_list = spotify.audio_features(recommended_track_ids)

    for track, track_audio_features in zip(song_recommendations['tracks'], track_audio_features_list):
        # Skip the song if it's already in the playlist
        if track['id'] in playlist_track_ids:
            continue
        track_info = {
            "Art": track["album"]["images"][0]["url"],
            "Artists": ", ".join(artist["name"] for artist in track["artists"]),
            "Song": track["name"],
            "Album": track["album"]["name"],
            "Key": pitch_names[track_audio_features['key']] if track_audio_features['key'] is not None else None,
            "URI": track["uri"],
        }
        for audio_feature in track_audio_features:
            if audio_feature not in ['type', 'id', 'track_href', 'analysis_url', 'key']:
                track_info[audio_feature] = track_audio_features[audio_feature]
        track_data.append(track_info)

    return track_data