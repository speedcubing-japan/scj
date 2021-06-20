from django.db import models


class StripeProgress(models.Model):

    customer_id = models.CharField('Stripe顧客ID', max_length=64)
    competition_id = models.IntegerField('大会ID', default=0)
    competitor_id = models.IntegerField('選手ID', default=0)
    charge_id = models.CharField('Stripe決済ID', max_length=256, default='')
    pay_price = models.IntegerField('支払額', default=0)
    refund_price = models.IntegerField('返金額', default=0)
    pay_at = models.DateTimeField('支払日時', default=None, null=True)
    refund_at = models.DateTimeField('返金日時', default=None, null=True)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        indexes = [
            models.Index(name='idx_customer_id', fields=['customer_id']),
            models.Index(name='idx_competitor_id', fields=['competitor_id'])
        ]