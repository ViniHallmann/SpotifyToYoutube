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

#LOAD DAS VARIAVEIS DO SPOTIFY NO .ENV
def get_spotify_variables_env():
    load_dotenv()
    return os.getenv("SPOTIFY_CLIENT_ID"), os.getenv("SPOTIFY_CLIENT_SECRET"), os.getenv("SPOTIFY_PLAYLIST_TRACKS")

#LOAD DAS VARIAVEIS DO YOUTUBE NO .ENV
def get_youtube_variables_env():
    load_dotenv()
    return os.getenv("YOUTUBE_CLIENT_ID"), os.getenv("YOUTUBE_CLIENT_SECRET")

#PEGANDO AS VARIAVEIS DO SPOTIFY E DO YOUTUBE
spotify_client_id, spotify_client_secret, spotify_saved_playlist = get_spotify_variables_env()
youtube_client_id, youtube_client_secret                         = get_youtube_variables_env()

# autenticando com o client_secret.json
SCOPES = ['https://www.googleapis.com/auth/youtube']
CLIENT_SECRETS_FILE = "client_secret.json"

#FUNÇÕES LADO YOUTUBE
"""
    FUNÇÃO PARA AUTENTICAR NO YOUTUBE
    AUTOR = Christian (Alemão) 
"""
def get_authenticated_service() -> str:
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_local_server(port=8080, prompt='consent', authorization_prompt_message='')
    return credentials

"""
    FUNÇÃO PARA BUSCAR MUSICA NO YOUTUBE -> RETORNA URL
    AUTOR = Christian (Alemão)
"""
def search_youtube(item) -> str:
    videosSearch = VideosSearch(item, limit=1)
    result = videosSearch.result()
    video_url = result['result'][0]['link']
    return video_url

"""
    FUNÇÃO PARA CRIAR PLAYLIST NO YOUTUBE CONFORME TITULO E DESCRIÇÃO NOS PARÂMETROS DA FUNÇÃO
    AUTOR = Christian (Alemão)
"""
def create_playlist(youtube, title, description) -> str:
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

"""
    FUNÇÃO PARA ADICIONAR MUSICA NA PLAYLIST DO YOUTUBE A PARTIR DO ID DA MUSICA E DA PLAYLIST
    AUTOR = Christian (Alemão)
"""    
def add_song_youtube(youtube, playlist_id, video_id) -> dict:  
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

#========================================================================================================================================================#
# FUNÇÕES LADO SPOTIFY
"""
    FUNÇÃO PARA PEGAR O TOKEN DE AUTOENTICAÇÃO DO SPOTIFY
    AUTOR = Vine
"""
def get_token() -> str:
    auth_string = f"{spotify_client_id}:{spotify_client_secret}"
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

"""
    FUNÇÃO PARA PEGAR HEADER DE AUTENTICAÇÃO DO SPOTIFY
    AUTOR = Vine
"""
def get_auth_header(token) -> dict:

    return {"Authorization": f"Bearer {token}"}

"""
    FUNÇÃO PARA PEGAR AS MÚSICAS DA PLAYLIST DO SPOTIFY
    AUTOR = Vine
"""
def get_playlist_tracks(token, playlist_id) -> list:

    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    next_url = json_result["tracks"]["next"]
    while next_url != None:
        if next_url is None: break
        result = get(next_url, headers=headers)
        json_result = json.loads(result.content)
        print(json_result["items"][0]["track"]["name"])
        next_url = json_result["next"]
    #return extract_track_info(json_result)

"""
    FUNÇÃO PARA EXTRAIR AS INFORMAÇÕES DAS MÚSICAS DA PLAYLIST DO SPOTIFY
    AUTOR = Vine e Christian
"""
def extract_track_info(playlist_json) -> list:

    """with open("playlist.json", "w") as file:
        json.dump(playlist_json, file, indent=4)
    """

    for item in playlist_json["tracks"]["items"]:
        if item["track"] is None:
            continue
        artist = item["track"]["artists"][0]["name"]
        title = item["track"]["name"]
        playlist_info.append({"artist": artist, "title": title})

    """for item in playlist_json["tracks"]["items"]:
        artist = item["track"]["artists"][0]["name"]
        title = item["track"]["name"]
        playlist_info.append({"artist": artist, "title": title})\
    """
        #artist_title_yt_search = (f"{title} - {artist}") # junta título da música e artista pra busca mais precisa no yt
        #ytLink = search_youtube(artist_title_yt_search) # procura a musica e salva o link 
        
        #if ytLink:
          #  video_id = ytLink.split("v=")[1].split("&")[0] # pega o id da musica com base no link 
          #  add_song_youtube(youtube, playlist_youtube_id, video_id) # adiciona a música a playlist definida na chamada da func
          #  playlist_info.append({"artist": artist, "title": title, "ytLink" : ytLink})
        
      #  else:
          #  print(f"Não foi possível encontrar um link para '{artist} - {title}' no YouTube.") # caso nao ache a musica 

    return playlist_info

"""
    FUNÇÃO PARA BUSCAR MUSICA NO YOUTUBE -> RETORNA PLAYLIST ATUALIZADA COM URL
    AUTOR = Vine
"""
def search_youtube_link(playlist_info) -> list:

    for item in playlist_info:
        artist_title_yt_search = (f"{item['title']} - {item['artist']}") # junta título da música e artista pra busca mais precisa no yt
        ytLink = search_youtube(artist_title_yt_search) # procura a musica e salva o link 
        
        if ytLink:
            item['ytLink'] = ytLink
        else:
            print(f"Não foi possível encontrar um link para '{item['artist']} - {item['title']}' no YouTube.") # caso nao ache a musica 

    return playlist_info

"""
    FUNÇÃO PARA ENVIAR AS MÚSICAS DA PLAYLIST DO SPOTIFY PARA O YOUTUBE
    AUTOR = Vine e Christian
"""
def send_to_youtube(playlist_info) -> None:
    for item in playlist_info:
        video_id = item['ytLink'].split("v=")[1].split("&")[0]     # Pega o ID da música com base no link 
        add_song_youtube(youtube, playlist_youtube_id, video_id)   # Adiciona a música a playlist definida na chamada da função
    return None

"""
    FUNÇÃO PARA SALVAR AS MÚSICAS DA PLAYLIST DO SPOTIFY NO .ENV
    AUTOR = Vine
"""
def save_to_env(playlist, id = None) -> None:

    playlist_tracks_str = json.dumps(playlist, ensure_ascii=False)
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    set_key(env_file, 'PLAYLIST_TRACKS', playlist_tracks_str)
    #set_key(env_file, "PLAYLIST_TRACKS", f"{id}=!=!={playlist_tracks_str}")
    return None

"""
    FUNÇÃO PARA VERIFICAR SE HÁ NOVAS MÚSICAS NA PLAYLIST DO SPOTIFY
    AUTOR = Vine
"""
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

#========================================================================================================================================================#
#YOUTUBE CONFIGS
"""
credentials = get_authenticated_service()                                   # autenticação no youtube
youtube = build('youtube', 'v3', credentials=credentials)                   # criação do objeto youtube
playlist_title = "Mandelão do FDS"                                          # titulo da playlist
description = "Só as boas"                                                  # descrição da playlist
playlist_youtube_id = create_playlist(youtube, playlist_title, description) # cria uma playlist com base nas config 
"""

#SPOTIFY CONFIGS
#3aJsKbVHL3U3ZngKqoVUZo?si=aa77820410b34402
playlist_id = "3aJsKbVHL3U3ZngKqoVUZo?si=aa77820410b34402"                            # id da playlist do spotify
#playlist_id = "2A49ff4cDR5xLqzg8L511Q?si=182bc5f9450e412a"                           # id da playlist do spotify
#playlist_tracks = get_playlist_tracks(get_token(), playlist_id, playlist_youtube_id) # pega as musicas da playlist do spotify
playlist_tracks = get_playlist_tracks(get_token(), playlist_id)                       # pega as musicas da playlist do spotify
#send_to_youtube(spotify_saved_playlist)

#save_to_env(playlist_tracks)                                                         # salva as musicas da playlist do spotify no .env
#has_new_music(playlist_tracks, playlist_id)                                          # verifica se há novas musicas na playlist do spotify

