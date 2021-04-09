
import logging
from music.utils import getMatchingVideo
import urllib
from music.models import Track

from django_cron import CronJobBase, Schedule

logger = logging.getLogger('music-cron')

class MusicCronJob(CronJobBase):

  Schedule(run_every_mins=5)

  def do():
    logger.info('Syncing Audio files with database')
    for track in Track.objects.all():
      query = urllib.parse.quote(track.name)
      getMatchingVideo(query)