from app import app
from flask import render_template, redirect, request, session, url_for, jsonify, send_from_directory, abort
import requests
import base64
import urllib
from dotenv import load_dotenv
import os
from suggest import generate_user_tracks
from create_playlist import create_playlist
from retrieve_playlists import get_user_playlists
from suggest_from_playlist import generate_playlist_tracks

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
REDIRECT_URI = os.getenv("REDIRECT_URI")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

@app.route('/')
def home(): #corresponds to home.html in templates
    return render_template('home.html')

@app.route('/discover')
def discover():
    return render_template("discover.html")

@app.route('/library')
def library():
    return render_template("library.html")

@app.route('/playlist_suggest')
def playlist_suggest():
    return render_template("suggest.html")

@app.route('/login')
def login():
    
    auth_url = "https://accounts.spotify.com/authorize"

    #Scope of user permissions
    scope = "user-library-read user-top-read playlist-modify-public playlist-read-private playlist-read-collaborative"

    #URL to redirect the user to
    auth_query_parameters = {
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": scope,
        # This ensures that the user sees the authorization prompt even if they've already authorized your app
        "show_dialog": True,
        "client_id": CLIENT_ID
    }

    url_args = "&".join(["{}={}".format(key, urllib.parse.quote(str(val))) for key, val in auth_query_parameters.items()])
    auth_url = "{}/?{}".format(auth_url, url_args)

    
    return redirect(auth_url)

#This is the route that Spotify will redirect to after the user logs in
@app.route('/callback')
def callback():
    # Get the authorization code that Spotify returned
    auth_token = request.args['code']

    # Request an access token using the authorization code
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI
    }
    base64encoded = base64.b64encode("{}:{}".format(CLIENT_ID, CLIENT_SECRET).encode())
    headers = {"Authorization": "Basic {}".format(base64encoded.decode())}
    post_request = requests.post("https://accounts.spotify.com/api/token", data=code_payload, headers=headers)

    # Get the access token from the response
    response_data = post_request.json()
    access_token = response_data["access_token"]

    # Save the access token in the user's session for later use
    session['access_token'] = access_token

    # Retrieve the Spotify username and profile picture
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get('https://api.spotify.com/v1/me', headers=headers)
    data = response.json()
    spotify_username = data['display_name']
    session['spotify_username'] = spotify_username

    if data['images']:
        spotify_profile_picture = data['images'][0]['url']
        session['spotify_profile_picture'] = spotify_profile_picture

    # Redirect the user to the most recent page or the home page if no recent page is found
    next_url = session.get('next_url', url_for('home'))
    return redirect(next_url)

@app.route('/generate_tracks', methods=['POST'])
def generate_tracks():
    # Get the access token from the request data
    access_token = request.json.get('access_token')
    if not access_token:
        return jsonify({'error': 'No access token provided'}), 400

    # Get the selected items from the dropdown menu
    selected_items = request.json.get('selected_items', [])

    # Call the function with the access token and selected items
    tracks = generate_user_tracks(access_token, selected_items)

    # Return the tracks as JSON
    return jsonify(tracks)

@app.route('/create_playlist', methods=['POST'])
def create_playlist_route():
    # Get the access token, playlist name, and tracks from the request data
    access_token = request.json.get('access_token')
    playlist_name = request.json.get('playlist_name')
    tracks = request.json.get('tracks')
    if not access_token or not playlist_name or not tracks:
        return jsonify({'error': 'No access token, playlist name, or tracks provided'}), 400

    # Call the function with the access token, playlist name, and tracks
    create_playlist(access_token, playlist_name, tracks)

    # Return a success message
    return jsonify({'message': 'Playlist created successfully'})

@app.route('/get_user_playlists', methods=['POST'])
def get_user_playlists_route():
    data = request.get_json()
    if 'access_token' in data and 'id' in data:
        access_token = data['access_token']
        user_id = data['id']

        playlists = get_user_playlists(access_token, user_id)

        return jsonify(playlists)
    else:
        return jsonify({'error': 'access_token or id not provided'}), 400
    

@app.route('/suggest_from_playlist', methods=['POST'])
def suggest_from_playlist():
    data = request.get_json()
    access_token = data.get('access_token')
    playlist_id = data.get('playlist_id')
    limit = data.get('limit', 50)  # Default to 50 if no limit is provided

    # Call the generate_playlist_tracks function
    tracks = generate_playlist_tracks(access_token, playlist_id, limit)

    # Return the tracks as a JSON response
    return jsonify(tracks)
