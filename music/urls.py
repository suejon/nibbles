from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'playlists', views.PlaylistViewSet)

urlpatterns = [
  path('', include(router.urls)),
  path('', views.index, name='index'),
  path('syncPlaylists', views.syncplaylists, name='syncPlaylists'),
  path('syncSongs', views.syncSongs, name='syncSongs'),
  path('syncContent', views.syncContent, name='syncContent')
]