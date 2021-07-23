from django.db import models
from app.defines.event import Event


class FeePerEvent(models.Model):

    competition_id = models.IntegerField('大会ID')
    event_id = models.SmallIntegerField('イベントID', choices=Event.choices())
    price = models.IntegerField('料金')
    prepaid_price = models.IntegerField('事前決済料金', default=0)

    def delete(competition_id):
        FeePerEvent.objects.filter(competition_id=competition_id).delete()

    def create(self, feeperevent, competition_id):
        self.competition_id = competition_id
        self.event_id = feeperevent['event_id']
        self.price = feeperevent['price']
        self.prepaid_price = feeperevent['prepaid_price']
        self.save()
