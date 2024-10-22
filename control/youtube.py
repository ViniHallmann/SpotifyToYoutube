from youtubesearchpython import VideosSearch
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from main     import get_youtube_variables_env

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
#def send_to_youtube(playlist_info) -> None:
    """
        FUNÇÃO PARA ENVIAR AS MÚSICAS DA PLAYLIST DO SPOTIFY PARA O YOUTUBE
        AUTOR = Vine e Christian
    """
 #   for item in playlist_info:
  #      video_id = item['ytLink'].split("v=")[1].split("&")[0]     # Pega o ID da música com base no link 
   #     add_song_youtube(youtube, playlist_youtube_id, video_id)   # Adiciona a música a playlist definida na chamada da função
    #return None
# =========================================


#  manda para o youtube adicionar usando o env
def send_links_to_youtube(env_links) -> None:
    """
        FUNÇÃO PARA ENVIAR OS LINKS DAS MÚSICAS DA PLAYLIST DO SPOTIFY PARA O YOUTUBE
        AUTOR = Vine e Christian
    """
    youtube_client_id, youtube_client_secret, youtube_links = get_youtube_variables_env()
    credentials = get_authenticated_service()
    playlist_youtube_id = "PLJx7IIF4C47C-p_1epjTOwMm4jlmRzrEu"    
    youtube = build('youtube', 'v3', credentials=credentials) 
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
        add_song_youtube(youtube, playlist_youtube_id, video_id)