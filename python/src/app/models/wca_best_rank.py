from django.db import models
from app.defines.event import Event


class WcaBestRank(models.Model):

    wca_id = models.CharField('WCA_ID', max_length=10)
    event_id = models.SmallIntegerField('イベントID', choices=Event.choices())
    best = models.IntegerField('ベスト')
    rank = models.IntegerField('順位')

    class Meta:
        indexes = [
            models.Index(name='idx_event_id_wca_id', fields=['event_id', 'wca_id'])
        ]