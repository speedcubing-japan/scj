from app.defines.gender import Gender
from app.defines.prefecture import Prefecture
from app.defines.event import Event
from app.defines.competitor import GENERATION_MAX
from django.shortcuts import render
from django.views.generic import TemplateView
from app.forms import RankingForm
from app.models import BestRank, AverageRank
from app.views.util.record import Record


class Index(TemplateView):
    def get(self, request):

        type = self.request.GET.get(key="type", default="best")
        event_id = int(self.request.GET.get(key="event_id", default=1))
        gender_id = int(self.request.GET.get(key="gender_id", default=0))
        generation_id = int(self.request.GET.get(key="generation_id", default=-1))
        prefecture_id = int(self.request.GET.get(key="prefecture_id", default=0))

        form = RankingForm(
            initial={
                "event_id": event_id,
                "generation_id": generation_id,
                "prefecture_id": prefecture_id,
                "gender_id": gender_id,
            }
        )

        form.fields["event_id"].choices = Event.choices()

        genders = [(0, "すべて")]
        genders += Gender.choices()

        form.fields["gender_id"].choices = tuple(genders)

        generattions = [(-1, "全世代")]
        for generation in range(0, GENERATION_MAX + 1):
            generattions.append(
                (generation * GENERATION_MAX, str(generation * GENERATION_MAX) + "代")
            )
        form.fields["generation_id"].choices = tuple(generattions)

        prefectures = [(0, "全都道府県")]
        prefectures += list(map(lambda x: (x.value, x.name), Prefecture))
        form.fields["prefecture_id"].choices = tuple(prefectures)

        if type == "best":
            ranks = BestRank.objects.order_by("rank")
        elif type == "average":
            ranks = AverageRank.objects.order_by("rank")

        if event_id != 0:
            ranks = ranks.filter(event_id=event_id)
        if gender_id != 0:
            ranks = ranks.filter(gender=gender_id)
        if generation_id != -1:
            ranks = ranks.filter(generation=generation_id)
        if prefecture_id != 0:
            ranks = ranks.filter(prefecture_id=prefecture_id)

        # 検索後のrankを再計算
        search_rank = 0
        before_rank = 0
        skip_count = 1
        for rank in ranks:
            if before_rank == 0 or before_rank < rank.rank:
                before_rank = rank.rank
                search_rank += skip_count
                skip_count = 1
            elif before_rank == rank.rank:
                skip_count += 1

            rank.rank = search_rank

            if type == "average":
                # 個々の結果表示を修正
                record = Record(
                    rank.value1,
                    rank.value2,
                    rank.value3,
                    rank.value4,
                    rank.value5,
                    rank.event_id
                )
                rank.format_values = record.format_values()

        context = {
            "ranks": ranks,
            "type": type,
            "form": form,
        }

        return render(request, "app/ranking/index.html", context)
