import datetime
from django.conf import settings
from django.template.loader import render_to_string


def make_post_text(data):
    open_at = data["open_at"]
    close_at = data["close_at"]
    registration_open_at = data["registration_open_at"]
    registration_close_at = data["registration_close_at"]

    if type(open_at) is str:
        open_at = datetime.datetime.fromisoformat(data["open_at"])
    if type(close_at) is str:
        close_at = datetime.datetime.fromisoformat(data["close_at"])

    if type(registration_open_at) is str:
        registration_open_at = datetime.datetime.fromisoformat(
            data["registration_open_at"]
        )
    if type(registration_close_at) is str:
        registration_close_at = datetime.datetime.fromisoformat(
            data["registration_close_at"]
        )

    weeks = ["月", "火", "水", "木", "金", "土", "日"]

    period = (
        open_at.strftime("%Y年%m月%d日")
        + "("
        + weeks[open_at.weekday()]
        + ") "
        + open_at.strftime("%H:%M")
        + " 〜 "
        + close_at.strftime("%H:%M")
    )

    registration_period = (
        registration_open_at.strftime("%Y年%m月%d日")
        + "("
        + weeks[registration_open_at.weekday()]
        + ") "
        + registration_open_at.strftime("%H:%M")
        + " 〜 "
        + registration_close_at.strftime("%Y年%m月%d日")
        + "("
        + weeks[registration_close_at.weekday()]
        + ") "
        + registration_close_at.strftime("%H:%M")
    )

    context = {
        "period": period,
        "registration_period": registration_period,
        "venue_name": data["venue_name"],
        "venue_address": data["venue_address"],
        "latitude": data["latitude"],
        "longitude": data["longitude"],
        "limit": data["limit"],
        "fee": data["fee"],
        "url": data["url"],
        "text": data["text"],
        "google_api_key": settings.GOOGLE_API_KEY,
        "google_map_url": settings.GOOGLE_MAP_URL,
    }

    return render_to_string("app/post/template.html", context).strip()
