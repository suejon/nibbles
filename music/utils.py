import configparser
import logging
import string
from pytube import YouTube

from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords

from datetime import date

import requests
from rest_framework.utils import json

from music.models import Track, Playlist

stopwords = stopwords.words('english')
logger = logging.getLogger('Utils')

def getproperty(section, key):
    config = configparser.ConfigParser()
    config.read('properties.ini')
    return config[section][key]

def getTracksFromPlaylist(remotePlaylist):
    playlist = Playlist.objects.filter(pk=remotePlaylist['id']).first()
    tracks = []
    if not playlist:
        print('no playlist with id')
        return tracks

    remoteTracks = remotePlaylist['tracks']['items']
    for t in remoteTracks:
        remoteTrack = t['track']
        # print(f'syncing track {remoteTrack["name"]}')
        # if 'artists' not in track:
        #     print(f'track {track["name"]} does not have an artist')
        artists = [str(artist['name']) for artist in remoteTrack['artists']]

        track = Track()
        track.id = remoteTrack['id']
        track.playlist = playlist
        track.artists = json.dumps(artists)
        track.album = remoteTrack['album']['name']
        track.name = remoteTrack['name']
        track.created_date = date.today()
        tracks.append(track)
    return tracks


def getVideoIdsFromSearch(query):
    config = configparser.ConfigParser()
    config.read('properties.ini')
    url = config['youtube']['url']

    response = requests.get(url + '/search' + f'?key={key}&q={query}')
    if response.status_code == 200:
        items = response.json()['items']
        video_ids = list(map(lambda x: x['id'], items))
        return video_ids
    return []


def getMatchingVideo(query):
    config = configparser.ConfigParser()
    config.read('properties.ini')
    url = config['youtube']['url']
    key = config['youtube']['api_key']

    video_ids = []

    response = requests.get(url + '/search' + f'?key={key}&q={query}')
    if response.status_code == 200:
        items = response.json()['items']
        video_ids = list(map(lambda x: x['id']['videoId'], items))
        download_audio(video_ids[0])
    else:
        print('Error in query for video IDs')
        return

def getBestMatch(items, text):
    scores = []

    for i in items:
        title = i['snippet']['title']
        to_compare = [clean_text(text), clean_text(title)]
        vectorizor = CountVectorizer().fit_transform(to_compare)
        vectors = vectorizor.toarray()
        cos_similarity = cosine_similarity(vectors[0].reshape(1,-1), vectors[1].reshape(1,-1))[0][0]
        scores.append(cos_similarity)

    index = scores.index(max(scores))

    print('get best match')
    print(f'scores: {scores}')
    print(f'max: {max(scores)}')
    print(f'max index: {scores.index(max(scores))}')
    print(items)
    print(items[index])

    return items[index]

def clean_text(text):
    text = ''.join([word for word in text if word not in string.punctuation])
    text = text.lower()
    text = ' '.join([word for word in text.split() if word not in stopwords])
    return text

def download_audio(video_id):
    config = configparser.ConfigParser()
    config.read('properties.ini')
    url = config['youtube']['public_url']
    destination_location = config['music']['destination_location']

    yt = YouTube(
        f'{url}/watch?v={video_id}',
        on_progress_callback=log_progress,
        on_complete_callback=log_completed)
    yt.streams.filter(only_audio=True).first().download(destination_location)

def log_progress(a,b,c):
    logger.info(f'Downloading')

def log_completed(a,b):
    logger.info(f'Download Complete')