#TUTORIAL SEGUIDO https://www.youtube.com/watch?v=WAmEZBEeNmg
from dotenv import load_dotenv, set_key
from requests import post
from requests import get
import os
import json
import base64
#Imports API GOOGLE
from youtubesearchpython import VideosSearch
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

playlist_info = []

#LOAD DO .ENV
def get_env():
    load_dotenv()
    return os.getenv("CLIENT_ID"), os.getenv("CLIENT_SECRET"), os.getenv("PLAYLIST_TRACKS")

client_id, client_secret, saved_playlist = get_env()

# autenticando com o client_secret.json
SCOPES = ['https://www.googleapis.com/auth/youtube']
CLIENT_SECRETS_FILE = "client_secret.json"

# func de autenticar o serviço google 
def get_authenticated_service():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_local_server(port=8080, prompt='consent', authorization_prompt_message='')
    return credentials

# function for search youtube music -> return url 
def search_youtube(item):
    videosSearch = VideosSearch(item, limit=1)
    result = videosSearch.result()
    video_url = result['result'][0]['link']
    return video_url

# cria a playlist conforme titulo e descrição informada na chamada da func
def create_playlist(youtube, title, description):
    request = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description
            },
            "status": {
                "privacyStatus": "public"
            }
        }
    )
    response = request.execute()
    return response['id']

# coloca a musica na playlist usando os ids
def add_song_youtube(youtube, playlist_id, video_id):
    request = youtube.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        }
    )
    response = request.execute()
    return response

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

def get_playlist_tracks(token, playlist_id, playlist_youtube_id) -> list:

    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)

    return extract_track_info(json_result, playlist_youtube_id)

def extract_track_info(playlist_json, playlist_youtube_id) -> list:
    for item in playlist_json["tracks"]["items"]:
        artist = item["track"]["artists"][0]["name"]
        title = item["track"]["name"]
        artist_title_yt_search = (f"{title} - {artist}") # junta título da música e artista pra busca mais precisa no yt
        ytLink = search_youtube(artist_title_yt_search) # procura a musica e salva o link 
        
        if ytLink:
            video_id = ytLink.split("v=")[1].split("&")[0] # pega o id da musica com base no link 
            add_song_youtube(youtube, playlist_youtube_id, video_id) # adiciona a música a playlist definida na chamada da func
            playlist_info.append({"artist": artist, "title": title, "ytLink" : ytLink})
        else:
            print(f"Não foi possível encontrar um link para '{artist} - {title}' no YouTube.") # caso nao ache a musica 

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
        if playlist_dumped != saved_playlist:
            print("New music detected!")
            return save_to_env(playlist, id)
        else:
            print("No new music detected.")
            return None
    else:
        print("No saved playlist found.")
    return None

# yt configs
credentials = get_authenticated_service() # autenticate the service
youtube = build('youtube', 'v3', credentials=credentials) # credentials and yt version
playlist_title = "Nova playlist Teste API" # titulo da playlist 
description = "Nova descrição teste"       # descrição da playlist
playlist_youtube_id = create_playlist(youtube, playlist_title, description) # cria uma playlist com base nas config 

# spotify configs
#3aJsKbVHL3U3ZngKqoVUZo?si=aa77820410b34402
playlist_id = "2A49ff4cDR5xLqzg8L511Q?si=182bc5f9450e412a"
playlist_tracks = get_playlist_tracks(get_token(), playlist_id, playlist_youtube_id) 
#save_to_env(playlist_tracks)
has_new_music(playlist_tracks, playlist_id)

