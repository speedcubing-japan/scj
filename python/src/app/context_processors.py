from django.conf import settings
from app.defines.competitor import Status as CompetitorStatus
from app.defines.fee import PayTypeEn as FeePayType
from app.defines.fee import CalcTypeEn as FeeCalcType
from app.defines.competition import Type as CompetitionType


def context_processor(req):
    return {
        "is_debug": settings.DEBUG,
        "competitor_status": CompetitorStatus.__members__,
        "fee_pay_type": FeePayType.__members__,
        "fee_calc_type": FeeCalcType.__members__,
        "competition_type": CompetitionType.__members__,
    }
