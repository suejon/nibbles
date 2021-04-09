from rest_framework import serializers
from .models import Playlist

class PlayListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Playlist
        fields = ['name', 'description', 'created_date', 'updated_date']