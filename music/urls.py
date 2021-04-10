from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'playlists', views.PlaylistViewSet)

urlpatterns = [
  path('', include(router.urls)),
  path('', views.index, name='index'),
  path('syncplaylists', views.syncplaylists, name='syncplaylists'),
  path('synccontent', views.synccontent, name='synccontent')
]