#TUTORIAL SEGUIDO https://www.youtube.com/watch?v=WAmEZBEeNmg
from flask import Flask, render_template, redirect, url_for, session
from dotenv import load_dotenv, set_key
from requests import post
from requests import get
import sys
import argparse
import os
import json
import base64
#Imports API GOOGLE
playlist_info = []

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')  # Carrega o index.html

#LOAD DAS VARIAVEIS DO SPOTIFY NO .ENV
def get_spotify_variables_env():
    load_dotenv()
    return os.getenv("SPOTIFY_CLIENT_ID"), os.getenv("SPOTIFY_CLIENT_SECRET")

#LOAD DAS VARIAVEIS DO YOUTUBE NO .ENV
def get_youtube_variables_env():
    load_dotenv()
    return os.getenv("YOUTUBE_CLIENT_ID"), os.getenv("YOUTUBE_CLIENT_SECRET"), os.getenv("YOUTUBE_TRACKS_LINKS")

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
    """
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
    """
if __name__ == '__main__':
    main()

#https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id=453623379966-kgilk354cg400s301bvs9ln2l9tmo96l.apps.googleusercontent.com&redirect_uri=http://localhost:5678/&scope=https://www.googleapis.com/auth/youtube&access_type=offline&prompt=consent