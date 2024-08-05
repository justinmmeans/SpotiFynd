import spotipy

def get_user_playlists(access_token, user_id):
    spotify = spotipy.Spotify(auth=access_token)
    playlists = spotify.user_playlists(user_id)
    
    for playlist in playlists['items']:
        print(playlist['name'])

    return playlists