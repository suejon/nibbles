from datetime import date, timezone

from django.db import models

class Playlist(models.Model):
  id = models.CharField(max_length=255, primary_key=True)
  name = models.CharField(max_length=50, null=False)
  description = models.CharField(max_length=255, null=True)
  created_date = models.DateField('date created', auto_created=True)
  updated_date = models.DateField('date updated', null=True)

class Location(models.Model):
  id = models.CharField(max_length=255, primary_key=True)
  path = models.FilePathField()
  created_date = models.DateField('date created', auto_created=True)
  updated_date = models.DateField('date updated', null=True)

class Track(models.Model):
  id = models.CharField(max_length=255, primary_key=True)
  name = models.CharField(max_length=255, null=True)
  album = models.CharField(max_length=255, null=True)
  artists = models.JSONField(encoder=None, null=True)
  playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
  location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
  created_date = models.DateField('date created', auto_created=True)
  video_id = models.CharField(max_length=255, null=True)
