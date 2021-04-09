from re import escape
import logging
import time
import urllib
from datetime import date
import schedule

from django.http import HttpResponse, HttpResponseNotFound
from rest_framework import permissions
from rest_framework import viewsets
import requests

from .utils import getMatchingVideo, getproperty, getTracksFromPlaylist
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
      print(f'have not seen this playlist id {id} before!')
      json = res.json()
      playlist = Playlist()
      playlist.id = json['id']
      playlist.name = json['name']
      playlist.description = json['description']
      playlist.created_date = date.today()
      playlist.save()
      print(f'Playlist [{playlist.name}] saved')
  return HttpResponse('Sync Completed')

def syncSongs(request):
  auth = Auth()
  url = getproperty('music', 'url')
  playlists = Playlist.objects.all()
  for p in playlists:
    res = requests.get(url=f'{url}/playlists/{p.id}', headers={'Authorization': f'Bearer {auth.get_access_token()}'})
    if res.status_code == 404:
      logger.error(f'Error getting playlist with id {id}, error: {res.json()}')
      continue

    tracks = getTracksFromPlaylist(res.json())
    if len(tracks) > 0:
      for t in tracks:
        if Track.objects.filter(pk=t.id).exists():
          logger.info(f'track id {id} already exists')
          continue
        logger.info(f'have not seen this track id {id} before')
        t.save()
  return HttpResponse("Success")


def syncContent(request):
  logger.info('Syncing Audio files with database')
  for track in Track.objects.all():
    query = urllib.parse.quote(track.name)
    getMatchingVideo(query)

  return HttpResponse(f'Synced {Track.objects.count()} tracks')

class PlaylistViewSet(viewsets.ModelViewSet):
  """
  API endpoint that allows Playlists to be viewed or edited
  """
  queryset = Playlist.objects.all().order_by('-created_date')
  serializer_class = PlayListSerializer
  permission_classes = [permissions.IsAuthenticated]
