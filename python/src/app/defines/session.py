from app.defines.define import Define
from enum import unique
from django.utils.translation import gettext_lazy as _


@unique
class Status(Define):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    DANGER = "danger"


@unique
class Notification(tuple, Define):
    UPDATE = (Status.INFO.value, "更新しました。")
    NOT_UPDATE = (Status.WARNING.value, "更新されていません。")
    RECAPTCHA_ERROR = (Status.DANGER.value, _("私はロボットではありませんにチェックを入れてください。"))
    RECAPTCHA_CONFIRM = (Status.INFO.value, _("この内容で登録します。よろしければチェックをいれて送信してください。"))
    REGISTRATION_CONFIRM = (Status.WARNING.value, "メールを確認して登録完了してください。")
    REGISTRATION_COMPLETE = (Status.SUCCESS.value, "ユーザー登録完了しました。")
    REGISTRATION_EXPIRED = (Status.DANGER.value, "ユーザー登録の期限切れです。再度ユーザー登録を行ってください。")
    REGISTRATION_BAD_SIGNATURE = (Status.DANGER.value, "不正な状態です。再度ユーザー登録を行ってください。")
    REGISTRATION_ALREADY_COMPLETED = (Status.WARNING.value, "既にユーザー登録を完了しています。")
    PASSWORD_CHANGE = (Status.SUCCESS.value, "パスワード変更しました。")
    PASSWORD_RESET = (Status.INFO.value, "パスワード変更の通知をメール送信しました。")
    MAIL_CHANGE = (Status.INFO.value, "メールアドレス変更通知をメール送信しました。")
    MAIL_CHANGE_COMPLETE = (Status.SUCCESS.value, "メールアドレスを変更しました。")
    CONTACT = (Status.SUCCESS.value, "お問い合わせを送信しました。")
    POST = (Status.SUCCESS.value, "お知らせを追加しました。")
    POST_OFFER = (Status.SUCCESS.value, "お知らせを申請しました。")
    POST_APPROVE = (Status.SUCCESS.value, "お知らせ申請を承認しました。")
    INFORMATION_DELETE = (Status.SUCCESS.value, "お知らせを削除しました。")
    PROFILE_CHANGE = (Status.SUCCESS.value, "プロフィールを更新しました。")
    WCA_AUTHORIZATION_COMPLETE = (Status.SUCCESS.value, "WCA認証が完了しました。")
    WCA_AUTHORIZATION_DUPLICATED = (
        Status.DANGER.value,
        "WCA IDが他アカウントと重複しています。認証に失敗しました。お問い合わせからご連絡ください。",
    )
    STRIPE_AUTHORIZATION_COMPLETE = (Status.SUCCESS.value, "Stripe認証が完了しました。")
    PAYMENT_SUCCESS = (Status.SUCCESS.value, "支払いが完了しました。")
    PAYMENT_CANCEL = (Status.WARNING.value, "支払いがキャンセルされました。")
    COMPETITION_LIMIT = (Status.DANGER.value, "承認人数が大会制限人数を超過しています。却下するか定員を増やしてください。")
    COMPETITION_PRIVATE = (Status.DANGER.value, _("この大会は非公開です。関係者のみ表示されます。"))
    COMPETITION_NOT_DISPLAY = (
        Status.WARNING.value,
        _("この大会は非表示です。一覧には表示されませんが、直接アクセスは可能です。管理等十分にお気をつけ下さい。"),
    )
    COMPETITION_CANCELED = (Status.DANGER.value, "この大会は中止になりました。")
    COMPETITION_REGISTER = (Status.SUCCESS.value, _("申し込み完了しました。承認されるまでお待ち下さい。"))
    COMPETITION_REGISTER_EDIT = (
        Status.SUCCESS.value,
        _("申し込み内容を更新しました。承認されるまでお待ち下さい。"),
    )
    COMPETITION_SCJ_END = (Status.INFO.value, "この大会は終了しました。結果が出るまでお待ち下さい。")
    COMPETITION_SCJ_HAS_RESULT_END = (Status.INFO.value, "この大会は終了しました。結果は結果タブをご覧ください。")
    COMPETITION_WCA_END = (Status.INFO.value, _("この大会は終了しました。"))
    COMPETITION_REGISTRATION_END = (Status.WARNING.value, _("この大会の申し込み受け付けは終了しました。"))
    COMPETITOR_PENGING = (Status.WARNING.value, _("あなたの申し込みは承認待ちです。"))
    COMPETITOR_REGISTRATION = (Status.SUCCESS.value, _("あなたの申し込みは承認されました。"))
    COMPETITOR_CANCEL = (Status.DANGER.value, "あなたの申し込みはキャンセルされました。")
    COMPETITOR_EVENT_NOT_SELECTED = (Status.WARNING.value, "種目が選択されていません。")
    REFUND_AMOUNT_OVER = (Status.WARNING.value, "全額よりも高い金額が設定されています。")
    REGISTRATION_PAY_SUCCESS = (
        Status.DANGER.value,
        _("大会参加費の支払いが成功しました。申し込みが登録されるまでお待ち下さい。再度お支払いいただく必要はありません。"),
    )
    REGISTRATION_PAY_CANCEL = (Status.DANGER.value, _("大会参加費の支払いがキャンセルされました。"))
    PERSON_INFO_CHANGE = (Status.SUCCESS.value, "ユーザ情報を更新しました。")
    COMPETITOR_RECEPTION_SUCCESS = (Status.SUCCESS.value, "参加者受付を行いました。")
    RECEPTION_SUCCESS = (Status.SUCCESS.value, "参加受付を完了しました。")
    GUEST_RECEPTION_SUCCESS = (Status.SUCCESS.value, "同伴者受付を行いました。")
    RECEPTION_CANCEL = (Status.DANGER.value, "参加者受付をキャンセルしました。")
    INVALID_RECEPTION_PAGE = (Status.DANGER.value, "この受付ページは無効です。")
    COMPETITON_NOT_REGISTRATION = (Status.DANGER.value, "この大会には申込されていません。")
    NOT_YET_RECEPTION = (Status.DANGER.value, "大会受付は当日のみ可能です。")
    RECEPTION_FINISHED = (Status.SUCCESS.value, "この大会は受付済みです。")
    SELF_RECEPTION_FINISHED = (Status.WARNING.value, "参加者受付済みです。同伴者受付をお願いします。")
    VISITOR_RECEPTION_SUCCESS = (Status.SUCCESS.value, "一般見学者数を更新しました。")
    SELF_RECEPTION_DIFFERENCE_PRICE = (Status.WARNING.value, "会場受付にて差分清算をお願いします。")
