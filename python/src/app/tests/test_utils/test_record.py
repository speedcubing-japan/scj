from django.test import TestCase
from app.models import Result, Round
from app.views.util.record import format_values


RESULT_DNF = -1
RESULT_DNS = -2


class RecordTestCase(TestCase):
    """format_valueテスト
    case1:
        競技: 333
        競技形態: ao5
        DNF数: 0
        DNS数: 0
    case2:
        競技: 333
        競技形態: ao5
        DNF数: 1
        DNS数: 0
    case3:
        競技: 333
        競技形態: ao5
        DNF数: 0
        DNS数: 1
    case4:
        競技: 333
        競技形態: ao5
        DNF数: 2
        DNS数: 0
    case5:
        競技: 333
        競技形態: ao5
        DNF数: 0
        DNS数: 2
    case6:
        競技: 333
        競技形態: ao5
        DNF数: 5
        DNS数: 0
    case7:
        競技: 333
        競技形態: ao5
        DNF数: 0
        DNS数: 5
    case8:
        競技: 333
        競技形態: ao5
        DNF数: 0
        DNS数: 0
        その他: best同タイム2つ
    case9:
        競技: 333
        競技形態: ao5
        DNF数: 0
        DNS数: 0
        その他: worst同タイム2つ
    """

    case1_answer = ["(20.74)", "18.72", "17.07", "(13.79)", "15.89"]
    case2_answer = ["20.74", "(DNF)", "17.07", "(13.79)", "15.89"]
    case3_answer = ["20.74", "18.72", "17.07", "(13.79)", "(DNS)"]
    case4_answer = ["(DNF)", "18.72", "DNF", "(13.79)", "15.89"]
    case5_answer = ["(DNS)", "18.72", "17.07", "(13.79)", "DNS"]
    case6_answer = ["(DNF)", "(DNF)", "(DNF)", "(DNF)", "(DNF)"]
    case7_answer = ["(DNS)", "(DNS)", "(DNS)", "(DNS)", "(DNS)"]
    case8_answer = ["(20.74)", "18.72", "17.07", "(13.79)", "13.79"]
    case9_answer = ["(20.74)", "18.72", "20.74", "(13.79)", "15.89"]

    def setUp(self):
        round_model = {
            "competition_id": 1,
            "event_id": 1,
            "attempt_count": 0,
            "type": 4,
            "format_id": 4,
            "limit_type": 1,
            "limit_time": 600,
            "cutoff_attempt_count": 0,
            "cutoff_time": 0,
            "proceed_count": 0,
            "room_name": "test",
        }
        case1_model = {
            "competition_id": 1,
            "event_id": 1,
            "person_id": 25,
            "round": Round.objects.create(**round_model),
            "rank": 1,
            "best": 13.79,
            "average": 17.23,
            "value1": 20.74,
            "value2": 18.72,
            "value3": 17.07,
            "value4": 13.79,
            "value5": 15.89,
        }
        case2_model = {
            "competition_id": 1,
            "event_id": 1,
            "person_id": 25,
            "round": Round.objects.create(**round_model),
            "rank": 1,
            "best": 13.79,
            "average": 17.23,
            "value1": 20.74,
            "value2": RESULT_DNF,
            "value3": 17.07,
            "value4": 13.79,
            "value5": 15.89,
        }
        case3_model = {
            "competition_id": 1,
            "event_id": 1,
            "person_id": 25,
            "round": Round.objects.create(**round_model),
            "rank": 1,
            "best": 13.79,
            "average": 17.23,
            "value1": 20.74,
            "value2": 18.72,
            "value3": 17.07,
            "value4": 13.79,
            "value5": RESULT_DNS,
        }
        case4_model = {
            "competition_id": 1,
            "event_id": 1,
            "person_id": 25,
            "round": Round.objects.create(**round_model),
            "rank": 1,
            "best": 13.79,
            "average": RESULT_DNF,
            "value1": RESULT_DNF,
            "value2": 18.72,
            "value3": RESULT_DNF,
            "value4": 13.79,
            "value5": 15.89,
        }
        case5_model = {
            "competition_id": 1,
            "event_id": 1,
            "person_id": 25,
            "round": Round.objects.create(**round_model),
            "rank": 1,
            "best": 13.79,
            "average": RESULT_DNF,
            "value1": RESULT_DNS,
            "value2": 18.72,
            "value3": 17.07,
            "value4": 13.79,
            "value5": RESULT_DNS,
        }
        case6_model = {
            "competition_id": 1,
            "event_id": 1,
            "person_id": 25,
            "round": Round.objects.create(**round_model),
            "rank": 1,
            "best": RESULT_DNF,
            "average": RESULT_DNF,
            "value1": RESULT_DNF,
            "value2": RESULT_DNF,
            "value3": RESULT_DNF,
            "value4": RESULT_DNF,
            "value5": RESULT_DNF,
        }
        case7_model = {
            "competition_id": 1,
            "event_id": 1,
            "person_id": 25,
            "round": Round.objects.create(**round_model),
            "rank": 1,
            "best": RESULT_DNS,
            "average": RESULT_DNF,
            "value1": RESULT_DNS,
            "value2": RESULT_DNS,
            "value3": RESULT_DNS,
            "value4": RESULT_DNS,
            "value5": RESULT_DNS,
        }
        case8_model = {
            "competition_id": 1,
            "event_id": 1,
            "person_id": 25,
            "round": Round.objects.create(**round_model),
            "rank": 1,
            "best": 13.79,
            "average": 17.23,
            "value1": 20.74,
            "value2": 18.72,
            "value3": 17.07,
            "value4": 13.79,
            "value5": 13.79,
        }
        case9_model = {
            "competition_id": 1,
            "event_id": 1,
            "person_id": 25,
            "round": Round.objects.create(**round_model),
            "rank": 1,
            "best": 13.79,
            "average": 17.23,
            "value1": 20.74,
            "value2": 18.72,
            "value3": 20.74,
            "value4": 13.79,
            "value5": 15.89,
        }
        self.case1 = Result.objects.create(**case1_model)
        self.case2 = Result.objects.create(**case2_model)
        self.case3 = Result.objects.create(**case3_model)
        self.case4 = Result.objects.create(**case4_model)
        self.case5 = Result.objects.create(**case5_model)
        self.case6 = Result.objects.create(**case6_model)
        self.case7 = Result.objects.create(**case7_model)
        self.case8 = Result.objects.create(**case8_model)
        self.case9 = Result.objects.create(**case9_model)

    def test_format_values(self):
        # case 1
        case1_result = format_values(self.case1)
        self.assertEqual(case1_result, self.case1_answer)

        # case 2
        case2_result = format_values(self.case2)
        self.assertEqual(case2_result, self.case2_answer)

        # case 3
        case3_result = format_values(self.case3)
        self.assertEqual(case3_result, self.case3_answer)

        # case 4
        case4_result = format_values(self.case4)
        self.assertEqual(case4_result, self.case4_answer)

        # case 5
        case5_result = format_values(self.case5)
        self.assertEqual(case5_result, self.case5_answer)

        # case 6
        case6_result = format_values(self.case6)
        self.assertEqual(case6_result, self.case6_answer)

        # case 7
        case7_result = format_values(self.case7)
        self.assertEqual(case7_result, self.case7_answer)

        # case 8
        case8_result = format_values(self.case8)
        self.assertEqual(case8_result, self.case8_answer)

        # case 9
        case9_result = format_values(self.case9)
        self.assertEqual(case9_result, self.case9_answer)
