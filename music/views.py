import json
import logging
import urllib
from datetime import date

from django.http import HttpResponse, HttpResponseNotFound
from rest_framework import permissions
from rest_framework import viewsets
import requests

from .utils import download_audio, getMatchingVideoId, getproperty, getTracksFromPlaylist
from .models import Playlist, Track
from .serializers import PlayListSerializer
from .auth import Auth

logger = logging.getLogger('Music')

def index(request):
  return HttpResponse("Welcome to the music index")

# @refresh_token
def syncplaylists(request):
  auth = Auth()
  url = getproperty('music', 'url')
  playlist_ids = getproperty('music', 'playlist_ids').split(',')
  for id in playlist_ids:
    res = requests.get(url=f'{url}/playlists/{id}', headers={'Authorization': f'Bearer {auth.get_access_token()}'})
    if res.status_code == 404:
      print(f'Error getting playlist with id {id}, error: {res.json()}')
      return HttpResponseNotFound(res.json())

    if not Playlist.objects.filter(pk=id).exists():
      print(f'Saving new playlist id {id}')
      json = res.json()
      playlist = Playlist()
      playlist.id = json['id']
      playlist.name = json['name']
      playlist.description = json['description']
      playlist.created_date = date.today()
      playlist.save()      
      print(f'Playlist [{playlist.name}] saved')
    playlist = Playlist.objects.filter(pk=id).first()
    synctracks(playlist.name, res.json())
  return HttpResponse('Sync Completed')

def synctracks(playlist_name, playlist_json):
  print(f'syncing tracks for playlist - {playlist_name}')
  tracks = getTracksFromPlaylist(playlist_json)
  if len(tracks) > 0:
    for t in tracks:
      if not None and not Track.objects.filter(pk=t.id).exists():
        print(f'Adding new track id {t.id}')
        t.save()
  return HttpResponse("Success")


def synccontent(request):
  unsynced = Track.objects.filter(downloaded=False).count()
  total = Track.objects.count()
  print(f'Syncing Audio files with database - total: {total}, synced: {total-unsynced}, unsynced: {unsynced}')
  download_destination = getproperty('music', 'destination_location')
  for track in Track.objects.filter(downloaded=False):
    param_artists = ' '.join(json.loads(track.artists)) # get all artist names in a space separated string
    query = urllib.parse.quote(f'{track.name} {param_artists}')
    videoId = getMatchingVideoId(query)
    if videoId != None:
      downloaded = download_audio(videoId, f'{download_destination}/{track.playlist.name}')
      if downloaded:
        track.downloaded = True
        track.save()
      else:
        print(f'Error downloading audio for query - {query}')

  return HttpResponse(f'Synced {unsynced} tracks ~!')

class PlaylistViewSet(viewsets.ModelViewSet):
  """
  API endpoint that allows Playlists to be viewed or edited
  """
  queryset = Playlist.objects.all().order_by('-created_date')
  serializer_class = PlayListSerializer
  permission_classes = [permissions.IsAuthenticated]
