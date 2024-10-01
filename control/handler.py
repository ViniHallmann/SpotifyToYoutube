#TUTORIAL SEGUIDO https://www.youtube.com/watch?v=WAmEZBEeNmg
from dotenv import load_dotenv, set_key
from requests import post
from requests import get
import sys
import argparse
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
    return os.getenv("SPOTIFY_CLIENT_ID"), os.getenv("SPOTIFY_CLIENT_SECRET")

#LOAD DAS VARIAVEIS DO YOUTUBE NO .ENV
def get_youtube_variables_env():
    load_dotenv()
    return os.getenv("YOUTUBE_CLIENT_ID"), os.getenv("YOUTUBE_CLIENT_SECRET"), os.getenv("YOUTUBE_TRACKS_LINKS")

#Autenticando com o client_secret.json
SCOPES = ['https://www.googleapis.com/auth/youtube']
CLIENT_SECRETS_FILE = "client_secret.json"

#FUNÇÕES LADO YOUTUBE
def get_authenticated_service() -> str:
    """
        FUNÇÃO PARA AUTENTICAR NO YOUTUBE
        AUTOR = Christian (Alemão) 
    """
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_local_server(port=8080, prompt='consent', authorization_prompt_message='')
    return credentials

def search_youtube(item) -> str:
    """
        FUNÇÃO PARA BUSCAR MUSICA NO YOUTUBE -> RETORNA URL
        AUTOR = Christian (Alemão)
    """
    videosSearch = VideosSearch(item, limit=1)
    result = videosSearch.result()
    video_url = result['result'][0]['link']
    return video_url

def create_playlist(youtube, title, description) -> str:
    """
        FUNÇÃO PARA CRIAR PLAYLIST NO YOUTUBE CONFORME TITULO E DESCRIÇÃO NOS PARÂMETROS DA FUNÇÃO
        AUTOR = Christian (Alemão)
    """
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
    print(response['id'])
    return response['id']
 
def add_song_youtube(youtube, playlist_id, video_id) -> dict:  
    """
        FUNÇÃO PARA ADICIONAR MUSICA NA PLAYLIST DO YOUTUBE A PARTIR DO ID DA MUSICA E DA PLAYLIST
        AUTOR = Christian (Alemão)
    """   
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

def search_youtube_link(playlist_info) -> list:
    """
        FUNÇÃO PARA BUSCAR MUSICA NO YOUTUBE -> RETORNA PLAYLIST ATUALIZADA COM URL
        AUTOR = Vine
    """
    for item in playlist_info:
        artist_title_yt_search = (f"{item['title']} - {item['artist']}") 
        ytLink = search_youtube(artist_title_yt_search) 
        print(ytLink)
        if ytLink:
            item['ytLink'] = ytLink
        else:
            print(f"Não foi possível encontrar um link para '{item['artist']} - {item['title']}' no YouTube.")

    return playlist_info


# adiciona com base nos itens da playlist
# INUTILIZADA =========================================
def send_to_youtube(playlist_info) -> None:
    """
        FUNÇÃO PARA ENVIAR AS MÚSICAS DA PLAYLIST DO SPOTIFY PARA O YOUTUBE
        AUTOR = Vine e Christian
    """
    for item in playlist_info:
        video_id = item['ytLink'].split("v=")[1].split("&")[0]     # Pega o ID da música com base no link 
        #add_song_youtube(youtube, playlist_youtube_id, video_id)   # Adiciona a música a playlist definida na chamada da função
    return None
# =========================================


#  manda para o youtube adicionar usando o env
def send_links_to_youtube(env_links) -> None:
    """
        FUNÇÃO PARA ENVIAR OS LINKS DAS MÚSICAS DA PLAYLIST DO SPOTIFY PARA O YOUTUBE
        AUTOR = Vine e Christian
    """
    cleaned_links = env_links.strip('[]')
    links_list = cleaned_links.split(", ")
    
    # Remova as aspas do primeiro e do último link, se necessário
    if links_list[0].startswith('"'):
        links_list[0] = links_list[0][1:]
    if links_list[-1].endswith('"'):
        links_list[-1] = links_list[-1][:-1]
    
    for link in links_list:
        link = link.strip('"')
        video_id = link.split("v=")[1].split("&")[0]
        #add_song_youtube(youtube, playlist_youtube_id, video_id)
     
#FUNÇÕES LADO SPOTIFY
def get_token() -> str:
    """
        FUNÇÃO PARA PEGAR O TOKEN DE AUTOENTICAÇÃO DO SPOTIFY
        AUTOR = Vine
    """
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

def get_auth_header(token) -> dict:
    """
        FUNÇÃO PARA PEGAR HEADER DE AUTENTICAÇÃO DO SPOTIFY
        AUTOR = Vine
    """
    return {"Authorization": f"Bearer {token}"}

def get_playlist_tracks(token, playlist_id) -> list:
    """
        FUNÇÃO PARA PEGAR AS MÚSICAS DA PLAYLIST DO SPOTIFY
        AUTOR = Vine
    """
    
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    next_url = json_result["tracks"]["next"]
    extract_track_info(json_result) 
    
    #json_result = get_json_result(token, playlist_id)
    next_url = json_result["tracks"]["next"]
    while next_url != None:
        if next_url == None: break
        result = get(next_url, headers=headers)
        json_result = json.loads(result.content)
        next_url = json_result["next"]
        extract_track_info(get_json_result(token, playlist_id)) 

    return playlist_info


def get_json_result(token, playlist_id) -> list:
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    return json_result

def get_playlist_name(token, playlist_id) -> list: 
    return get_json_result(token, playlist_id)["name"]

def get_playlist_description(token, playlist_id) -> list:
    return get_json_result(token, playlist_id)["description"]

def format_url_into_id(url): 
    # https://open.spotify.com/playlist/3aJsKbVHL3U3ZngKqoVUZo?si=477510c34f704fea
    try:
        start = url.index("playlist/") + len("playlist/")
        id = url[start:]
        return id
    except ValueError:
        return "Id não encontrado"

def extract_track_info(playlist_json) -> None:
    """
        FUNÇÃO PARA EXTRAIR AS INFORMAÇÕES DAS MÚSICAS DA PLAYLIST DO SPOTIFY
        AUTOR = Vine e Christian
    """
    if "tracks" in playlist_json: 
        for item in playlist_json["tracks"]["items"]:
            if item["track"] is None:
                continue
            else: 
                artist = item["track"]["artists"][0]["name"]
                title = item["track"]["name"]
                playlist_info.append({"artist": artist, "title": title})
    else: 
        for item in playlist_json["items"]:
            if item["track"] is None:
                continue
            else: 
                artist = item["track"]["artists"][0]["name"]
                title = item["track"]["name"]
                playlist_info.append({"artist": artist, "title": title})

def save_to_env(playlist, id = None) -> None:
    """
        FUNÇÃO PARA SALVAR AS MÚSICAS DA PLAYLIST DO SPOTIFY NO .ENV
        AUTOR = Vine
    """
    playlist_tracks_str = json.dumps(playlist, ensure_ascii=False)
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    set_key(env_file, 'SPOTIFY_PLAYLIST_TRACKS', playlist_tracks_str)
    return None

def extract_links(playlist) -> list:
    """
    FUNÇÃO PARA EXTRAIR OS LINKS DAS MÚSICAS DA PLAYLIST
    AUTOR = Vine
    """
    links = [item['ytLink'] for item in playlist if 'ytLink' in item]
    return links

def save_links_to_env(links) -> None:
    """
    FUNÇÃO PARA SALVAR OS LINKS DAS MÚSICAS EM UM NOVO .ENV
    AUTOR = Vine
    """
    links_str = json.dumps(links, ensure_ascii=False)
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    set_key(env_file, 'SPOTIFY_TRACKS_LINKS', links_str)
    return None

def has_new_music(id: str = None) -> str:
    """
        FUNÇÃO PARA VERIFICAR SE HÁ NOVAS MÚSICAS NA PLAYLIST DO SPOTIFY
        AUTOR = Vine e Christian
    """
    return id
    #saved_playlist = os.getenv("PLAYLIST_TRACKS")
    #playlist_dumped = json.dumps(playlist, ensure_ascii=False)

    """if saved_playlist:
        if playlist_dumped != saved_playlist:
            print("New music detected!")
            return save_to_env(playlist, id)
        else:
            print("No new music detected.")
            return None
    else:
        print("No saved playlist found.")"""
    return None

#========================================================================================================================================================#
#YOUTUBE CONFIGS
#"""

#"""
playlist_youtube_id = "PLJx7IIF4C47C-p_1epjTOwMm4jlmRzrEu"

spotify_client_id, spotify_client_secret = get_spotify_variables_env()
youtube_client_id, youtube_client_secret, youtube_links = get_youtube_variables_env()

#SPOTIFY CONFIGS
"""
playlist_id = "3aJsKbVHL3U3ZngKqoVUZo?si=aa77820410b34402"                            # id da playlist do spotify
playlist_tracks = get_playlist_tracks(get_token(), playlist_id)                      # pega as musicas da playlist do spotify
search_youtube_link(playlist_info)
links = extract_links(playlist_info)
save_links_to_env(links)
"""

#"""
#send_links_to_youtube(youtube_links)
#send_to_youtube(spotify_saved_playlist)
#save_to_env(playlist_tracks)                                                         # salva as musicas da playlist do spotify no .env
#has_new_music(playlist_tracks, playlist_id)                                          # verifica se há novas musicas na playlist do spotify

def return_playlist_id():
    playlist_youtube_id = "PLJx7IIF4C47C-p_1epjTOwMm4jlmRzrEu"
    return playlist_youtube_id

#python3 /usr/local/scripts/main.py has_new_music {{workflow.variables['playlist_id']}} {{node['HTTP Request'].json['access_token']}}

def main():
    credentials = get_authenticated_service()                     
    youtube = build('youtube', 'v3', credentials=credentials) 

    spotify_token = get_token()

    parser = argparse.ArgumentParser(description='Run specific function from the script.')
    parser.add_argument('function', type=str, help='The function to run')
    parser.add_argument('playlist_id', type=str, nargs='?', default=None, help='Playlist ID')
    parser.add_argument('token', type=str, help='OAuth2 Access Token')
    
    args = parser.parse_args()

    youtube = build('youtube', 'v3', credentials=args.token) 
    if args.function == 'return_playlist_id':
        result = return_playlist_id()

    elif args.function == "create_playlist":
        create_playlist(youtube, get_playlist_name(spotify_token, args.playlist_id), get_playlist_description(spotify_token, args.playlist_id))

    elif args.function == 'get_playlist_tracks':
        get_playlist_tracks(spotify_token, return_playlist_id()) 
        playlist_name = get_playlist_name(spotify_token, return_playlist_id())
        print(f"Musicas resgatadas da playlist: '{playlist_name}'")

    elif args.function == 'has_new_music':
        result = has_new_music(args.playlist_id)
        print(result)
    else:
        print(f"Function '{args.function}' not found")
    
if __name__ == '__main__':
    main()

#https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id=453623379966-kgilk354cg400s301bvs9ln2l9tmo96l.apps.googleusercontent.com&redirect_uri=http://localhost:5678/&scope=https://www.googleapis.com/auth/youtube&access_type=offline&prompt=consent