from app.models import FeePerEvent, FeePerEventCount
from app.defines.fee import CalcTypeEn as FeeCalcTypeEn


def calc_fee(competition, competitor):
    fees = {}
    prepaid_fees = {}
    price = 0

    if competition.fee_calc_type == FeeCalcTypeEn.EVENT.value:
        results = FeePerEvent.objects.filter(competition_id=competition.id)
        for result in results:
            fees[result.event_id] = result.price
            prepaid_fees[result.event_id] = result.prepaid_price

        if competitor:
            for result in results:
                if result.event_id == 0:
                    price += result.prepaid_price
                if result.event_id in competitor.event_ids:
                    price += result.prepaid_price

    elif competition.fee_calc_type == FeeCalcTypeEn.EVENT_COUNT.value:
        results = FeePerEventCount.objects.filter(competition_id=competition.id)
        for result in results:
            fees[result.event_count] = result.price
            prepaid_fees[result.event_count] = result.prepaid_price

        if competitor:
            event_count = len(competitor.event_ids)
            for result in results:
                if result.event_count == 0:
                    price += result.prepaid_price
                if result.event_count == event_count:
                    price += result.prepaid_price

    return {"fees": fees, "prepaid_fees": prepaid_fees, "price": price}
