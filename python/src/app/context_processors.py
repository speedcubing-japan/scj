from django.conf import settings
from app.defines.competitor import Status as CompetitorStatus
from app.defines.fee import PayTypeEn as FeePayType
from app.defines.fee import CalcTypeEn as FeeCalcType
from app.defines.competition import Type as CompetitionType
from app.defines.competition import RoundLimitType as RoundLimitType
from app.defines.competition import ProceedType as ProceedType


def context_processor(req):
    return {
        "is_debug": settings.DEBUG,
        "competitor_status": CompetitorStatus.__members__,
        "fee_pay_type": FeePayType.__members__,
        "fee_calc_type": FeeCalcType.__members__,
        "competition_type": CompetitionType.__members__,
        "round_limit_type": RoundLimitType.__members__,
        "proceed_type": ProceedType.__members__,
    }
