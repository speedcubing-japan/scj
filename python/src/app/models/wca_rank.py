from django.db import models
from app.defines.record import Type as RecordType
from app.defines.event import Event


class WcaRank(models.Model):

    wca_id = models.CharField("WCA_ID", max_length=10)
    event_id = models.SmallIntegerField("イベントID", choices=Event.choices())
    type = models.SmallIntegerField("レコードタイプ", choices=RecordType.choices())
    best = models.FloatField("ベスト")
    world_rank = models.IntegerField("世界ランク", default=0)
    continent_rank = models.IntegerField("大陸ランク", default=0)
    country_rank = models.IntegerField("国ランク", default=0)
    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    class Meta:
        indexes = [
            models.Index(name="idx_wca_id_event_id", fields=["wca_id", "event_id"])
        ]

    def create(wca_id, event_id, type, best, world_rank, continent_rank, country_rank):
        self = WcaRank()
        self.wca_id = wca_id
        self.event_id = event_id
        self.type = type
        self.best = best
        self.world_rank = world_rank
        self.continent_rank = continent_rank
        self.country_rank = country_rank
        return self

    def delete_by_wca_id(wca_id):
        WcaRank.objects.filter(wca_id=wca_id).delete()

    def get_by_wca_ids_and_event_id(wca_ids, event_id):
        return WcaRank.objects.filter(wca_id__in=wca_ids, event_id=event_id)
