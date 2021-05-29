import configparser
import logging
import string
from pytube import YouTube

# from sklearn.metrics.pairwise import cosine_similarity
# from sklearn.feature_extraction.text import CountVectorizer
# from nltk.corpus import stopwords

from datetime import date

import requests
from rest_framework.utils import json

from music.models import Track, Playlist

# stopwords = stopwords.words('english')
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

def getMatchingVideoId(query, track):
    if track.video_id:
        return track.video_id

    config = configparser.ConfigParser()
    config.read('properties.ini')
    url = config['youtube']['url']
    key = config['youtube']['api_key']

    response = requests.get(url + '/search' + f'?key={key}&q={query}')
    if response.status_code == 200:
        items = response.json()['items']
        for i in items:
            if 'videoId' in i['id']:
                return i['id']['videoId']
    if response.status_code == 403:
        print('Hitting too many times, exiting')
        exit()

    print(f'Could not find any videos for query - {query}, response: {response}')
    return None

# def getBestMatch(items, text):
#     scores = []

#     for i in items:
#         title = i['snippet']['title']
#         to_compare = [clean_text(text), clean_text(title)]
#         vectorizor = CountVectorizer().fit_transform(to_compare)
#         vectors = vectorizor.toarray()
#         cos_similarity = cosine_similarity(vectors[0].reshape(1,-1), vectors[1].reshape(1,-1))[0][0]
#         scores.append(cos_similarity)

#     index = scores.index(max(scores))

#     print('get best match')
#     print(f'scores: {scores}')
#     print(f'max: {max(scores)}')
#     print(f'max index: {scores.index(max(scores))}')
#     print(items)
#     print(items[index])

#     return items[index]

# def clean_text(text):
#     text = ''.join([word for word in text if word not in string.punctuation])
#     text = text.lower()
#     text = ' '.join([word for word in text.split() if word not in stopwords])
#     return text

def getArtistNames(arists_json):
    json = json.load(arists_json)


def download_audio(track, video_id, destination_path):
    url = getproperty('youtube', 'public_url')

    try:
        yt = YouTube(
            f'{url}/watch?v={video_id}',
            on_complete_callback=log_completed)
        print(f' Downloading: song - {track.name}, link - {url}/watch?v={video_id}')
        audio = yt.streams.filter(only_audio=True).first()
        if audio is None:
            return False
        audio.download(destination_path)
    except Exception as e:
        print(e)
        return False

    return True

def log_completed(a,b):
    print(f'Download Complete')

def getPlaylistIds():
    playlistIds = []
    with open('playlists.txt') as f:
        playlistIds = [line.rstrip('\n') for line in f]
    return playlistIds
