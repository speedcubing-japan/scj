import datetime
import re
import pprint
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from app.models import Person, User, Post, Information
from django.conf import settings
from django.core.mail import BadHeaderError, send_mail
from django.http import HttpResponse
from django.utils import timezone
from app.consts import PREFECTURE, INFORMATION_TYPE, INFORMATION_TYPE_EVENT

class UserCreateForm(UserCreationForm):

    class Meta:
        model = User
        fields = (
            'email', 
            'password1', 
            'password2'
        )
        help_texts = {
            'email': '使用可能なメールアドレスを入力してください。',
        }
    
    def clean_email(self):
        email = self.cleaned_data['email']
        User.objects.filter(email=email, is_active=False).delete()
        return email

class PersonCreateForm(forms.ModelForm):

    class Meta:
        model = Person
        fields = (
            'last_name', 
            'last_name_kana', 
            'last_name_roma', 
            'first_name',
            'first_name_kana',
            'first_name_roma',
            'gender', 
            'birth_at',
            'prefecture_id',
        )
        error_messages = {
            'last_name': {
                'max_length': '姓が不正です。'
            },
            'first_name': {
                'max_length': '名が不正です。'
            },
            'last_name_kana': {
                'max_length': 'セイが不正です。'
            },
            'first_name_kana': {
                'max_length': 'メイが不正です。'
            },
            'last_name_roma': {
                'max_length': '姓(ローマ字)が不正です。'
            },
            'first_name_roma': {
                'max_length': '名(ローマ字)が不正です。'
            },
        }
        help_texts = {
            'last_name': '漢字でお願いします。(例:荒木) 海外籍の方はlastNameを入力してください。',
            'last_name_kana': '全角カタカナでお願いします。(例:アラキ) 海外籍の方もカタカナで入力してください。',
            'last_name_roma': 'ローマ字でお願いします。(例:Araki) 海外籍の方も入力してください。',
            'first_name': '漢字でお願いします。(例:慎平) 海外籍の方はfirstNameを入力してください。',
            'first_name_kana': '全角カタカナでお願いします。(例:シンペイ) 海外籍の方もカタカナで入力してください。',
            'first_name_roma': 'ローマ字でお願いします。(例:Shimpei) 海外籍の方も入力してください。',
            'prefecture_id': '海外籍の方は海外を選択してください。',
        }
        widgets = {
            'birth_at': forms.SelectDateWidget(years=range(datetime.date.today().year + 1, 1900, -1))
        }

    def clean_first_name_kana(self):
        first_name_kana = self.cleaned_data['first_name_kana']
        re_katakana = re.compile(r'[\u30A1-\u30F4]+')
        if not re_katakana.fullmatch(first_name_kana):
            raise forms.ValidationError('全角カタカナでない文字が含まれています。')
        return first_name_kana

    def clean_last_name_kana(self):
        last_name_kana = self.cleaned_data['last_name_kana']
        re_katakana = re.compile(r'[\u30A1-\u30F4]+')
        if not re_katakana.fullmatch(last_name_kana):
            raise forms.ValidationError('全角カタカナでない文字が含まれています。')
        return last_name_kana

    def clean_first_name_roma(self):
        first_name_roma = self.cleaned_data['first_name_roma']
        if re.fullmatch('[a-zA-Z]+', first_name_roma) == None:
            raise forms.ValidationError('半角アルファベットでない文字が含まれています。')
        if first_name_roma != first_name_roma.capitalize():
            raise forms.ValidationError('先頭文字が大文字、それ以降の文字は小文字でお願いします。')
        return first_name_roma

    def clean_last_name_roma(self):
        last_name_roma = self.cleaned_data['last_name_roma']
        if re.fullmatch('[a-zA-Z]+', last_name_roma) == None:
            raise forms.ValidationError('アルファベットでない文字が含まれています。')
        if last_name_roma != last_name_roma.capitalize():
            raise forms.ValidationError('先頭文字が大文字、それ以降の文字は小文字でお願いします。')
        return last_name_roma

class LoginForm(AuthenticationForm):
    pass

class PasswordChangeForm(PasswordChangeForm):

    class Meta:
        model = User

class PasswordResetForm(PasswordResetForm):

    class Meta:
        model = User
    
    def clean_email(self):
        email = self.cleaned_data['email']
        query = User.objects.filter(email=email)
        if not query.exists():
            raise forms.ValidationError('メールアドレスが存在しません。')
        return email

class SetPasswordForm(SetPasswordForm):
    
    class Meta:
        model = User

class MailChangeForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('email',)

    def clean_email(self):
        email = self.cleaned_data['email']
        User.objects.filter(email=email, is_active=False).delete()
        return email

class ContactForm(forms.Form):
    name = forms.CharField(
        label='お名前',
        max_length=100,
    )
    email = forms.EmailField(
        label='メールアドレス'
    )
    message = forms.CharField(
        label='お問い合わせ内容',
        widget=forms.Textarea
    )

    def send_email(self):
        subject = 'お問い合わせ'
        message = self.cleaned_data['message']
        name = self.cleaned_data['name']
        email = self.cleaned_data['email']
        
        message = '名前: ' + name + '\r\n' + 'メールアドレス: ' + email + '\r\n\r\n' + message

        from_email = settings.EMAIL_HOST_USER
        recipient_list = ['info@speedcubing.or.jp', '1c181577.speedcubing.or.jp@jp.teams.ms']  # 受信者リスト
        try:
            send_mail(subject, message, from_email, recipient_list)
        except BadHeaderError:
            return HttpResponse('無効なヘッダが検出されました。')

class ProfileForm(forms.Form):
    prefecture_id = forms.fields.ChoiceField(
        label='都道府県',
        label_suffix='',
        widget=forms.widgets.Select,
        choices=PREFECTURE
    )

class CompetitionForm(forms.Form):
    type = forms.fields.ChoiceField(
        label='大会種別',
        label_suffix='',
        widget=forms.widgets.Select
    )
    event_id = forms.fields.ChoiceField(
        label='開催種目',
        label_suffix='',
        widget=forms.widgets.Select
    )
    year = forms.fields.ChoiceField(
        label='開催年',
        label_suffix='',
        widget=forms.widgets.Select
    )
    prefecture_id = forms.fields.ChoiceField(
        label='開催都道府県',
        label_suffix='',
        widget=forms.widgets.Select
    )

class CompetitionRegistrationForm(forms.Form):
    event_ids = forms.MultipleChoiceField(
          label='参加種目',
          required=True,
          widget=forms.CheckboxSelectMultiple(attrs=
          {
               'id': 'event_ids'
          })
    )
    guest_count = forms.fields.ChoiceField(
        label='見学者数',
        required=True,
        widget=forms.widgets.Select,
    )
    comment = forms.fields.CharField(
        label='コメント',
        required=False,
        widget=forms.Textarea(attrs={'cols': '80', 'rows': '5'}),
    )
    name_id = forms.fields.CharField(
        widget=forms.HiddenInput()
    )

class CompetitionAdminCompetitorEditForm(forms.Form):
    event_ids = forms.MultipleChoiceField(
          label='参加種目',
          required=True,
          widget=forms.CheckboxSelectMultiple(attrs=
          {
               'id': 'event_ids'
          })
    )
    name_id = forms.fields.CharField(
        widget=forms.HiddenInput()
    )
    competitor_id = forms.fields.CharField(
        widget=forms.HiddenInput()
    )

class PostForm(forms.Form):
    title = forms.CharField(
        label='タイトル',
        required=True,
        max_length=24,
    )
    open_at = forms.DateTimeField(
        label='開始日時',
        required=True,
        widget=forms.DateTimeInput(attrs={"type": "datetime-local", "value": timezone.datetime.now().strftime('%Y-%m-%dT%H:%M')}),
        input_formats=['%Y-%m-%dT%H:%M']
    )
    close_at = forms.DateTimeField(
        label='終了日時',
        required=True,
        widget=forms.DateTimeInput(attrs={"type": "datetime-local", "value": timezone.datetime.now().strftime('%Y-%m-%dT%H:%M')}),
        input_formats=['%Y-%m-%dT%H:%M']
    )
    registration_open_at = forms.DateTimeField(
        label='申し込み開始日時',
        required=True,
        widget=forms.DateTimeInput(attrs={"type": "datetime-local", "value": timezone.datetime.now().strftime('%Y-%m-%dT%H:%M')}),
        input_formats=['%Y-%m-%dT%H:%M']
    )
    registration_close_at = forms.DateTimeField(
        label='申し込み終了日時',
        required=True,
        widget=forms.DateTimeInput(attrs={"type": "datetime-local", "value": timezone.datetime.now().strftime('%Y-%m-%dT%H:%M')}),
        input_formats=['%Y-%m-%dT%H:%M']
    )
    venue_name = forms.CharField(
        label='開催地名',
        required=True,
        max_length=256,
    )
    venue_address = forms.CharField(
        label='開催地住所',
        required=True,
        max_length=256,
    )
    latitude = forms.CharField(
        label='開催地緯度',
        required=True,
        max_length=256,
    )
    longitude = forms.CharField(
        label='開催地経度',
        required=True,
        max_length=256,
    )
    limit = forms.IntegerField(
        label='制限人数',
        required=True,
    )
    fee = forms.IntegerField(
        label='参加費',
        required=True,
    )
    url = text = forms.CharField(
        label='URL',
        required=True,
        max_length=256,
    )
    text = forms.CharField(
        label='自由入力',
        required=False,
        widget=forms.Textarea(attrs={'cols': '80', 'rows': '5'}),
        max_length=512,
    )

class PostEditForm(forms.Form):
    title = forms.CharField(
        label='タイトル',
        required=True,
        max_length=24,
    )
    text = forms.CharField(
        label='本文',
        required=True,
        widget=forms.Textarea(attrs={'cols': '80', 'rows': '10'}),
    )

class InformationForm(forms.ModelForm):

    class Meta:
        model = Information
        fields = ('type', 'title', 'text', 'is_public')

class RankingForm(forms.Form):
    event_id = forms.fields.ChoiceField(
        label='種目',
        label_suffix='',
        widget=forms.widgets.Select
    )
    gender_id = forms.fields.ChoiceField(
        label='性別',
        label_suffix='',
        widget=forms.widgets.Select
    )
    generation_id = forms.fields.ChoiceField(
        label='世代別',
        label_suffix='',
        widget=forms.widgets.Select
    )
    prefecture_id = forms.fields.ChoiceField(
        label='都道府県',
        label_suffix='',
        widget=forms.widgets.Select
    )