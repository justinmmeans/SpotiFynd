import spotipy

def get_user_playlists(access_token, user_id):
    spotify = spotipy.Spotify(auth=access_token)
    playlists = spotify.current_user_playlists()
    
    for playlist in playlists['items']:
        print(playlist['name'])

    return playlists