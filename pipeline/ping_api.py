#!/usr/bin/env python
import json
import requests
from kafka import KafkaProducer
from flask import Flask, request

app = Flask(__name__)
producer = KafkaProducer(bootstrap_servers='kafka:29092')

def query_playlist():
    
    CLIENT_ID = '<id_here>'
    CLIENT_SECRET = '<secret_here'
    AUTH_URL = 'https://accounts.spotify.com/api/token'

    auth_response = requests.post(AUTH_URL, {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    })
    
    auth_response_data = auth_response.json()
    access_token = auth_response_data['access_token']
    
    headers = {
        'Authorization': 'Bearer {token}'.format(token=access_token)
    }
    
    r = requests.get('https://api.spotify.com/v1/playlists/37i9dQZEVXbMDoHDwVN2tF', headers=headers)
    
    return r.json()

def log_to_kafka(topic, event):
    event.update(request.headers)
    producer.send(topic, json.dumps(event).encode())

@app.route("/")
def default_response():
    default_event = {'playlist_details': query_playlist()}
    log_to_kafka('playlists', default_event)
    return "Playlist Queried!\n"