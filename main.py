#TUTORIAL SEGUIDO https://www.youtube.com/watch?v=WAmEZBEeNmg
from dotenv import load_dotenv, set_key
from requests import post
from requests import get
import os
import json
import base64
playlist_info = []
#LOAD DO .ENV
def get_env():
    load_dotenv()
    return os.getenv("CLIENT_ID"), os.getenv("CLIENT_SECRET"), os.getenv("PLAYLIST_TRACKS")

client_id, client_secret, saved_playlist = get_env()

def get_token() -> str:

    auth_string = f"{client_id}:{client_secret}"
    auth_bytes = auth_string.encode('utf-8')
    auth_base64 = str(base64.b64encode(auth_bytes), 'utf-8')
    
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {auth_base64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}

    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_auth_header(token) -> dict:

    return {"Authorization": f"Bearer {token}"}

def get_playlist_tracks(token, playlist_id) -> list:

    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)

    return extract_track_info(json_result)

def extract_track_info(playlist_json) -> list:

    for item in playlist_json["tracks"]["items"]:
        artist = item["track"]["artists"][0]["name"]
        title = item["track"]["name"]
        playlist_info.append({"artist": artist, "title": title})
    return playlist_info

def save_to_env(playlist, id = None) -> None:

    playlist_tracks_str = json.dumps(playlist, ensure_ascii=False)
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    set_key(env_file, 'PLAYLIST_TRACKS', playlist_tracks_str)
    #set_key(env_file, "PLAYLIST_TRACKS", f"{id}=!=!={playlist_tracks_str}")
    return None

def has_new_music(playlist, id) -> None:
    saved_playlist = os.getenv("PLAYLIST_TRACKS")
    playlist_dumped = json.dumps(playlist, ensure_ascii=False)

    if saved_playlist:
        if playlist != saved_playlist:
            print("New music detected!")
            return save_to_env(playlist, id)
        else:
            print("No new music detected.")
            return None
    else:
        print("No saved playlist found.")
    return None


#3aJsKbVHL3U3ZngKqoVUZo?si=aa77820410b34402
playlist_id = "2A49ff4cDR5xLqzg8L511Q?si=182bc5f9450e412a"
playlist_tracks = get_playlist_tracks(get_token(), playlist_id)
#save_to_env(playlist_tracks)
has_new_music(playlist_tracks, playlist_id)

