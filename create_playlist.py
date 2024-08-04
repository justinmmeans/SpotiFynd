from flask import Flask, request, jsonify
import spotipy

def create_playlist(access_token, playlist_name, tracks, limit=50):
    spotify = spotipy.Spotify(auth=access_token)

    # Get the user's username
    user = spotify.me()['id']

    # Create the playlist
    playlist = spotify.user_playlist_create(user, playlist_name)

    # Get the track URIs from the tracks
    track_uris = [track['URI'] for track in tracks]

    # Add the tracks to the playlist
    spotify.playlist_add_items(playlist['id'], track_uris)

    return tracks