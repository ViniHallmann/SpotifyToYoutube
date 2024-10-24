#TUTORIAL SEGUIDO https://www.youtube.com/watch?v=WAmEZBEeNmg
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import os
from dotenv import load_dotenv
from requests import post
from requests import get
import sys
import argparse
import json
import base64

from youtube import get_authenticated_service, build_youtube_service, search_youtube_link, create_playlist, send_links_to_youtube
from spotify import get_token, get_playlist_tracks, get_playlist_name, get_playlist_description, format_url_into_id
#Imports API GOOGLE
app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Necessário para usar sessions
load_dotenv()

# Variáveis OAuth
CLIENT_ID = os.getenv('YOUTUBE_CLIENT_ID')
CLIENT_SECRET = os.getenv('YOUTUBE_CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:5000/oauth2callback'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/playlist', methods=['POST'])
def playlist():
    data = request.get_json()
    playlist_url = data.get('playlist')

    if playlist_url:
        # Salva a playlist no session
        session['playlist_url'] = playlist_url

        # Gera o URL de autenticação do Google OAuth
        auth_url = (
            f'https://accounts.google.com/o/oauth2/v2/auth?response_type=code'
            f'&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}'
            f'&scope=https://www.googleapis.com/auth/youtube'
            f'&access_type=offline&prompt=consent'
        )

        # Retorna o URL de redirecionamento ao frontend
        return jsonify({'redirect_url': auth_url})
    else:
        return jsonify({'error': 'Invalid playlist URL'}), 400

@app.route('/oauth2callback')
def oauth2callback():
    code = request.args.get('code')
    if code:
        # Troca do código por um token de acesso
        token_url = 'https://oauth2.googleapis.com/token'
        token_data = {
            'code': code,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'redirect_uri': REDIRECT_URI,
            'grant_type': 'authorization_code',
        }
        response = post(token_url, data=token_data)
        token_info = response.json()

        # Processa a resposta e manipula a playlist
        playlist_url = session.get('playlist_url')
        sp_playlist_id = format_url_into_id(playlist_url)
        print(sp_playlist_id)

        spotify         = get_token(spotify_client_id, spotify_client_secret)
        sp_playlist_info   = get_playlist_tracks(spotify, sp_playlist_id)
        sp_playlist_name   = get_playlist_name(spotify, sp_playlist_id)
        sp_playlist_desc   = get_playlist_description(spotify, sp_playlist_id)

        #YOUTUBE SIDE
        youtube             = build_youtube_service()
        playlist_info       = search_youtube_link(sp_playlist_info)
        yt_playlist_id      = create_playlist(youtube, sp_playlist_name, sp_playlist_desc)
        send_links_to_youtube(youtube, yt_playlist_id, playlist_info)
        
        """
        if playlist_url and 'access_token' in token_info:
            access_token = token_info['access_token']
            # Aqui você pode adicionar lógica para manipular a playlist do YouTube usando o token
            return f'Autenticação bem-sucedida! Playlist: {playlist_url}'
        else:
            return 'Erro ao obter o token de acesso.', 400
            """
    else:
        return 'Erro na autenticação.', 400

#LOAD DAS VARIAVEIS DO SPOTIFY NO .ENV
def get_spotify_variables_env():
    return os.getenv("SPOTIFY_CLIENT_ID"), os.getenv("SPOTIFY_CLIENT_SECRET")

#LOAD DAS VARIAVEIS DO YOUTUBE NO .ENV
def get_youtube_variables_env():
    return os.getenv("YOUTUBE_CLIENT_ID"), os.getenv("YOUTUBE_CLIENT_SECRET"), os.getenv("YOUTUBE_TRACKS_LINKS")

#========================================================================================================================================================#

playlist_youtube_id = "PLJx7IIF4C47C-p_1epjTOwMm4jlmRzrEu"

spotify_client_id, spotify_client_secret = get_spotify_variables_env()
youtube_client_id, youtube_client_secret, youtube_links = get_youtube_variables_env()

def get_playlist_id():
    #return "3aJsKbVHL3U3ZngKqoVUZo"
    return "2A49ff4cDR5xLqzg8L511Q"

def main():
    #WORKFLOW: -> RUN MAIN -> GET_BUILD -> GET_TOKEN -> GET_PLAYLIST_TRACKS -> GET_TRACKS_INFO 
    #          -> GET_YOUTUBE_LINKS -> GET_YOUTUBE_ID -> GET_YOUTUBE_PLAYLIST -> GET_YOUTUBE_TRACKS 
    #          -> GET_YOUTUBE_TRACKS_INFO -> ADD_YOUTUBE_TRACKS -> RETURN
    #SPOTIFY SIDE
    app.run()
    """
    spotify         = get_token(spotify_client_id, spotify_client_secret)
    sp_playlist_id  = get_playlist_id()
    sp_playlist_info   = get_playlist_tracks(spotify, sp_playlist_id)
    sp_playlist_name   = get_playlist_name(spotify, sp_playlist_id)
    sp_playlist_desc   = get_playlist_description(spotify, sp_playlist_id)

    #YOUTUBE SIDE
    youtube             = build_youtube_service()
    playlist_info       = search_youtube_link(sp_playlist_info)
    yt_playlist_id      = create_playlist(youtube, sp_playlist_name, sp_playlist_desc)
    send_links_to_youtube(youtube, yt_playlist_id, playlist_info)
    """
    pass

if __name__ == '__main__':
    main()

#https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id=453623379966-kgilk354cg400s301bvs9ln2l9tmo96l.apps.googleusercontent.com&redirect_uri=http://localhost:5678/&scope=https://www.googleapis.com/auth/youtube&access_type=offline&prompt=consent