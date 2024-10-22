import json
import base64
import os
from requests import get, post
from dotenv   import load_dotenv, set_key

playlist_info = []

def get_token(spotify_client_id, spotify_client_secret) -> str:
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
    
    if result.status_code != 200:
        print(f"Erro ao obter o token: {result.status_code}, {result.content}")
        return None
    
    json_result = json.loads(result.content)

    token = json_result.get("access_token")
    if not token:
        print("Erro: 'access_token' não encontrado na resposta.")
        return None
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

def format_url_into_id(url) -> str: 
    """
    Função para formatar a URL da playlist do Spotify em um ID
    """
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

"""def save_to_env(playlist, id = None) -> None:

    playlist_tracks_str = json.dumps(playlist, ensure_ascii=False)
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    set_key(env_file, 'SPOTIFY_PLAYLIST_TRACKS', playlist_tracks_str)
    return None

def extract_links(playlist) -> list:

    links = [item['ytLink'] for item in playlist if 'ytLink' in item]
    return links

def save_links_to_env(links) -> None:

    links_str = json.dumps(links, ensure_ascii=False)
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    set_key(env_file, 'SPOTIFY_TRACKS_LINKS', links_str)
    return None"""

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