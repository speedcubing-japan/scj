import json
import pyjq
import requests
import pprint
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.conf import settings
from django.views.generic import View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class WcaAbout(TemplateView):
    template_name = 'app/wca/about.html'

class WcaHoldingPolicy(TemplateView):
    template_name = 'app/wca/holding_policy.html'

class WcaRegulation(TemplateView):
    template_name = 'app/wca/regulation.html'

class WcaRanking(TemplateView):
    template_name = 'app/wca/ranking.html'

class WcaAuthorization(TemplateView):
    def get(self, request):

        code = self.request.GET.get('code')
        type = self.request.GET.get('type')

        if code == None or type == None:
            return redirect('index')

        current_site = get_current_site(self.request)
        domain = current_site.domain
        protocol = 'https' if self.request.is_secure() else 'http'

        redirect_uri = protocol + '://' + domain + '/wca/authorization/?type=' + type
        if type == 'competition':
            if request.session.get('wca_authorization_name_id') is None:
                return redirect('index')
            name_id = request.session.get('wca_authorization_name_id')

        params = {
            'grant_type': 'authorization_code',
            'client_id': settings.WCA_CLIENT_ID,
            'client_secret': settings.WCA_CLIENT_SECRET,
            'code': code,
            'redirect_uri': redirect_uri
        }

        response = requests.post(settings.WCA_OAUTH_TOKEN_URL, params)
        if response.status_code == requests.codes.ok:
            access_token = response.json()['access_token']
            refresh_token = response.json()['refresh_token']
            headers = {'Authorization': 'Bearer ' + access_token}
            response = requests.get(settings.WCA_API_URL, headers=headers)

            if response.status_code == requests.codes.ok:

                wca_id = ''
                if response.json()['me']['wca_id']:
                    wca_id = response.json()['me']['wca_id']

                if request.user.is_authenticated and request.user.person:
                    person = request.user.person
                    person.wca_id = wca_id
                    person.wca_user_id = response.json()['me']['id']
                    person.wca_email = response.json()['me']['email']
                    person.wca_name = response.json()['me']['name']
                    person.wca_country_iso2 = response.json()['me']['country_iso2']
                    person.wca_access_token = access_token
                    person.wca_refresh_token = refresh_token
                    person.wca_avatar_url = response.json()['me']['avatar']['url']
                    person.wca_avatar_thumb_url = response.json()['me']['avatar']['thumb_url']
                    person.save(update_fields=[
                        'wca_id',
                        'wca_user_id',
                        'wca_email',
                        'wca_name',
                        'wca_country_iso2',
                        'wca_access_token',
                        'wca_refresh_token',
                        'wca_avatar_url',
                        'wca_avatar_thumb_url',
                        'updated_at'
                    ])

                request.session['notification'] = 'is_just_wca_authorization_complete'

                if type == 'competition':
                    del self.request.session['notification']
                    return redirect('competition_detail', name_id=name_id)      

                return redirect(type)

        return redirect('index')