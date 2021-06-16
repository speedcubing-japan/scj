import app.consts
from app.defines.competitor import Status as CompetitorStatus
from app.defines.fee import PayTypeEn as FeePayType
from app.defines.fee import CalcTypeEn as FeeCalcType

def context_processor(req):
    return {
        'consts': app.consts,
        'competitor_status': CompetitorStatus.__members__,
        'fee_pay_type': FeePayType.__members__,
        'fee_calc_type': FeeCalcType.__members__
    }