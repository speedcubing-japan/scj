from django.db import models


class FeePerEventCount(models.Model):

    competition_id = models.IntegerField('大会ID')
    event_count = models.SmallIntegerField('イベント数')
    price = models.IntegerField('料金')
    prepaid_price = models.IntegerField('事前決済料金', default=0)

    def delete(competition_id):
        FeePerEventCount.objects.filter(competition_id=competition_id).delete()

    def create(self, feepereventcount, competition_id):
        self.competition_id = competition_id
        self.event_count = feepereventcount['event_count']
        self.price = feepereventcount['price']
        self.prepaid_price = feepereventcount['prepaid_price']
        self.save()