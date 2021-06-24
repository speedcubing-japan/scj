from django.db import models
from app.defines.event import Event


class FeePerEvent(models.Model):

    competition_id = models.IntegerField('大会ID')
    event_id = models.SmallIntegerField('イベントID', choices=Event.choices())
    price = models.IntegerField('料金')
    prepaid_price = models.IntegerField('事前決済料金', default=0)