import json
import stripe
import datetime
from django.conf import settings
from django.http import HttpResponse
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from app.models import Competition, Competitor, StripeProgress, Person
from app.views.competition.util import send_mail
from app.defines.fee import PayTypeEn as FeePayType
from app.defines.competitor import Status as CompetitorStatus


@method_decorator(csrf_exempt, name="dispatch")
class WebhookConnect(View):
    def post(self, request):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe_webhook_endpoint_secret = (
            settings.STRIPE_WEBHOOK_CONNECT_ENDPOINT_SECRET_KEY
        )

        payload = request.body.decode("utf-8")
        sig_header = request.META["HTTP_STRIPE_SIGNATURE"]

        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, stripe_webhook_endpoint_secret
            )
        except ValueError:
            # Invalid payload
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError:
            # Invalid signature
            return HttpResponse(status=400)

        if event.type == "payment_intent.succeeded":
            payment_intent = event.data.object
            # 基本一つだけ。
            charges = payment_intent.charges.data[0]
            now = datetime.datetime.fromtimestamp(
                charges.created, tz=datetime.timezone.utc
            )

            # 決済が存在していた場合は支払い済み。
            if StripeProgress.exist_charge_id(self, charges.id):
                return HttpResponse(status=200)

            competition = Competition.objects.get(pk=charges.metadata.competition_id)
            if competition.fee_pay_type == FeePayType.REMOTE_ONLY.value:

                # 競技者が存在していた場合支払い済み。
                if Competitor.exist(
                    self, charges.metadata.competition_id, charges.metadata.person_id
                ):
                    return HttpResponse(status=200)

                # Person情報取得
                person = Person.objects.get(pk=charges.metadata.person_id)
                # 参加登録
                comment = ""
                if "comment" in charges.metadata:
                    comment = charges.metadata.comment

                competitor = Competitor()
                competitor.create(
                    charges.metadata.competition_id,
                    CompetitorStatus.PENDING.value,
                    json.loads(charges.metadata.event_ids),
                    charges.metadata.guest_count,
                    comment,
                    person,
                )
                # 作成時間をchargeのcreateに合わせる。作成時はauto_now_addのために現在時刻が適用されてしまうため。
                competitor.update_created_at(now)

            elif competition.fee_pay_type == FeePayType.LOCAL_AND_REMOTE.value:
                competitor = Competitor.objects.get(pk=charges.metadata.competitor_id)

            stripe_progress = StripeProgress()
            stripe_progress.customer_id = charges.customer
            stripe_progress.competition_id = charges.metadata.competition_id
            stripe_progress.competitor_id = competitor.id
            stripe_progress.charge_id = charges.id
            stripe_progress.pay_price = charges.amount
            stripe_progress.pay_at = now
            stripe_progress.save()

            send_mail(
                request,
                competitor.person.user,
                competition,
                "app/mail/competition/registration_payment_subject.txt",
                "app/mail/competition/registration_payment_message.txt",
                price=charges.amount,
            )

        return HttpResponse(status=200)
