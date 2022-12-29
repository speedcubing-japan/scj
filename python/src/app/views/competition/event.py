from django.utils.timezone import localtime
from django.shortcuts import render
from app.models import Round
from .base import Base


class Event(Base):

    template_name = "app/competition/event.html"

    def get(self, request, **kwargs):
        return render(request, self.template_name, self.get_context())

    def get_context(self):
        context = super().get_context()

        rounds = Round.objects.filter(competition_id=self.competition.id).order_by(
            "begin_at"
        )
        # 日付 -> 会場 -> record
        round_dict = {}
        for round in rounds:
            date = localtime(round.begin_at).strftime("%Y年%m月%d日")
            if date not in round_dict:
                round_dict[date] = {}

            if round.room_name in round_dict[date]:
                round_dict[date][round.room_name].append(round)
            else:
                round_dict[date].update({round.room_name: [round]})

        # 種目ごとにラウンドを分ける(FMCが複数レコードある)
        event_round_types = {}
        for round in rounds:
            if round.event_id > 0:
                if round.event_id in event_round_types:
                    event_round_types[round.event_id].add(round.type)
                else:
                    event_round_types[round.event_id] = set([round.type])

        event_round_count_dict = {}
        for event_id, round_types in event_round_types.items():
            event_round_count_dict[event_id] = len(round_types)

        # 作成時のエラー
        admin_errors = self.request.session.get("competition_admin_errors")
        if self.request.session.get("competition_admin_errors") is not None:
            del self.request.session["competition_admin_errors"]

        context["round_dict"] = round_dict
        context["event_round_count_dict"] = event_round_count_dict
        context["admin_errors"] = admin_errors

        return context
