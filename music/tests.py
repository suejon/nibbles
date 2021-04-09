from django.test import TestCase
from .views import syncplaylists

# Create your tests here.

class MusicTest(TestCase):

    def test_syncplaylists(self):
        syncplaylists()