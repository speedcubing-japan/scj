import csv
from io import TextIOWrapper
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from app.models import Competition, Round, FeePerEvent, FeePerEventCount
from app.defines.fee import CalcTypeEn as FeeCalcType
from app.defines.session import Notification
from app.views.competition.base import Base
from app.views.competition.util import (
    check_competition,
    check_round,
    check_feeperevent,
    check_feepereventcount,
)


class Edit(LoginRequiredMixin, Base):
    errors = []

    def get(self, request, **kwargs):
        return redirect("competition_detail", name_id=self.name_id)

    def post(self, request, **kwargs):
        self.errors = []

        for file in request.FILES.getlist("file"):
            form_data = TextIOWrapper(file.file, encoding="utf-8")
            reader = csv.DictReader(form_data)
            datas = [row for row in reader]

            if "competition.csv" in file.name:
                if len(datas) != 1:
                    self.errors.append("csvファイルが2行でないです。ヘッダーも含めます。")
                else:
                    data = datas[0]

                    self.errors.extend(check_competition(data, "update"))
                    if data["name_id"] != self.name_id:
                        self.errors.append(
                            "name_idが一致しません。csvファイルが間違っている可能性があります。name_idを変更する場合は、削除して作り直して下さい。"
                        )

                if self.errors:
                    request.session["competition_admin_errors"] = set(self.errors)
                else:
                    competition = Competition.objects.get(name_id=self.name_id)
                    competition.update(data)
                    self.save_notification(Notification.UPDATE)

                return redirect("competition_detail", name_id=self.name_id)

            if "round.csv" in file.name:
                for line, data in enumerate(datas):
                    self.errors.extend(
                        check_round(line, data, self.competition.event_ids)
                    )

                if self.errors:
                    request.session["competition_admin_errors"] = set(self.errors)
                else:
                    # 全消しして再度追加する
                    Round.delete(self.competition.id)
                    for data in datas:
                        round = Round()
                        round.create(data, self.competition.id)

                    self.save_notification(Notification.UPDATE)

                return redirect("competition_schedule", name_id=self.name_id)

            if "feeperevent.csv" in file.name:
                if self.competition.fee_calc_type == FeeCalcType.EVENT.value:
                    for line, data in enumerate(datas):
                        self.errors.extend(
                            check_feeperevent(line, data, self.competition.event_ids)
                        )

                    # 全体チェック
                    contains_base_fee = False
                    for data in datas:
                        if int(data["event_id"]) == 0:
                            contains_base_fee = True

                    if not contains_base_fee:
                        self.errors.append("base_fee(event_id = 0)が設定されていません。")
                else:
                    self.errors.append("competitionのfee_calc_typeがEVENTではないです。")

                if self.errors:
                    request.session["competition_admin_errors"] = set(self.errors)
                else:
                    # 全消しして再度追加する
                    FeePerEvent.delete(self.competition.id)
                    FeePerEventCount.delete(self.competition.id)
                    for data in datas:
                        feeperevent = FeePerEvent()
                        feeperevent.create(data, self.competition.id)

                    self.save_notification(Notification.UPDATE)

                return redirect("competition_fee", name_id=self.name_id)

            if "feepereventcount.csv" in file.name:
                if self.competition.fee_calc_type == FeeCalcType.EVENT_COUNT.value:
                    for line, data in enumerate(datas):
                        self.errors.extend(check_feepereventcount(line, data))

                    # 全体チェック
                    contains_base_fee = False
                    for data in datas:
                        if int(data["event_count"]) == 0:
                            contains_base_fee = True

                    if not contains_base_fee:
                        self.errors.append("base_fee(event_count = 0)が設定されていません。")
                else:
                    self.errors.append("competitionのfee_calc_typeがEVENT_COUNTではないです。")

                if self.errors:
                    request.session["competition_admin_errors"] = set(self.errors)
                else:
                    # 全消しして再度追加する
                    FeePerEvent.delete(self.competition.id)
                    FeePerEventCount.delete(self.competition.id)
                    for data in datas:
                        feepereventcount = FeePerEventCount()
                        feepereventcount.create(data, self.competition.id)

                    self.save_notification(Notification.UPDATE)

                return redirect("competition_fee", name_id=self.name_id)

            self.errors.append(
                "ファイル名が規定外です。大会データはcompetition.csv、スケジュールラウンドデータはround.csv、料金データはfeeperevent.csvまたはfeepereventcount.csvをアップロードしてください。"
            )
            request.session["competition_admin_errors"] = set(self.errors)

        return redirect("competition_detail", name_id=self.name_id)
