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

from youtube import get_authenticated_service, build_youtube_service, search_youtube_link, create_playlist, send_links_to_youtube
from spotify import get_token, get_playlist_tracks, get_playlist_name, get_playlist_description
#Imports API GOOGLE
playlist_info = []

app = Flask(__name__)
load_dotenv()
@app.route('/')
def index():
    return render_template('index.html')  # Carrega o index.html

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

    pass

if __name__ == '__main__':
    main()

#https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id=453623379966-kgilk354cg400s301bvs9ln2l9tmo96l.apps.googleusercontent.com&redirect_uri=http://localhost:5678/&scope=https://www.googleapis.com/auth/youtube&access_type=offline&prompt=consent