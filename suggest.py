import collections
import spotipy
import json
import os

pitch_names = ['C', 'C#/Db', 'D', 'D#/Eb', 'E', 'F', 'F#/Gb', 'G', 'G#/Ab', 'A', 'A#/Bb', 'B']

def generate_user_tracks(access_token, limit=50):
    
    spotify = spotipy.Spotify(auth=access_token)
    
    #Retrieves the user's saved tracks from cache for quicker access
    home_dir = os.path.expanduser("~")

    #Save json file to the cache file in project root.
    cache_file = os.path.join('cache', 'saved_tracks_cache.json')

    if os.path.exists(cache_file):
        # Load tracks from cache file
        with open(cache_file, 'r') as f:
            saved_tracks = json.load(f)
    else:
        # Retrieve tracks from Spotify API and save to cache file
        saved_tracks = []
        results = spotify.current_user_saved_tracks()
        saved_tracks.extend(results['items'])
        while results['next']:
            results = spotify.next(results)
            saved_tracks.extend(results['items'])
        # Ensure the cache directory exists
        os.makedirs(os.path.dirname(cache_file), exist_ok=True)
        with open(cache_file, 'w') as f:
            json.dump(saved_tracks, f)

    saved_track_ids = set(track['track']['id'] for track in saved_tracks)

    #Retrieve the user's top tracks up to 100 songs
    top_tracks = spotify.current_user_top_tracks(time_range='medium_term', limit=50)
    top_track_ids = [track['id'] for track in top_tracks['items']]

    #Get the artist IDs from the top tracks
    artist_ids = [track['artists'][0]['id'] for track in top_tracks['items']]

    #Get information about all user saved artists
    artists = spotify.artists(artist_ids)

    #Get the genres of their artists
    top_artist_genres = [artist['genres'] for artist in artists['artists']]

    #Find the most common genres. The amount for this + seeded tracks must = 5
    flattened_genres = [genre for genres in top_artist_genres for genre in genres]
    #(number) + seeded_tracks cannot exceed 5
    most_common_genre = collections.Counter(flattened_genres).most_common(1)[0][0] 

    #Combine seeds for song recommendations [:#] value corresponds to weight. These values + most_common_genre cannot exceed 5
    seeded_tracks = (list(saved_track_ids)[:1] + top_track_ids[:3])

    # Retrieve song recommendations based on track and genre seeds
    # Retrieve song recommendations based on track and genre seeds
    song_recommendations = spotify.recommendations(seed_tracks=seeded_tracks, seed_genres=[most_common_genre], limit=50)

    # Prepare the data for output
    track_data = []
    recommended_tracks = [track for track in song_recommendations['tracks'] if track['id'] not in saved_track_ids and track['id'] not in top_track_ids]

    # Get all features in one API call
    recommended_track_ids = [track['id'] for track in recommended_tracks]
    track_audio_features_list = spotify.audio_features(recommended_track_ids)

    for track, track_audio_features in zip(recommended_tracks, track_audio_features_list):
        # Add the track to be output
        track_info = {
            "Art": track["album"]["images"][0]["url"],
            "Artists": ", ".join(artist["name"] for artist in track["artists"]),
            "Song": track["name"],
            "Album": track["album"]["name"],  
            "URI": track["uri"], 
        }
        for audio_feature in track_audio_features:
            if audio_feature not in ['type', 'id', 'track_href', 'analysis_url']:
                if audio_feature == 'key' and track_audio_features[audio_feature] is not None:
                    track_info[audio_feature] = pitch_names[track_audio_features[audio_feature]]
                else:
                    track_info[audio_feature] = track_audio_features[audio_feature]
        track_data.append(track_info)

    # Return the list of track data
    return track_data