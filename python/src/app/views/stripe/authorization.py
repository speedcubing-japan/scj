import requests
from django.conf import settings
from django.shortcuts import redirect
from django.views.generic import View


class Authorization(View):
    def get(self, request):

        if not request.user.is_authenticated or not request.user.person.is_judge:
            return redirect('index')

        code = self.request.GET.get('code')
        if code == None:
            return redirect('index')

        params = {
            'grant_type': 'authorization_code',
            'client_secret': settings.STRIPE_SECRET_KEY,
            'code': code,
        }

        response = requests.post(settings.STRIPE_OAUTH_TOKEN_URL, params)
        if response.status_code == requests.codes.ok:
            stripe_user_id = response.json()['stripe_user_id']

            person = request.user.person
            person.stripe_user_id = stripe_user_id
            person.save(update_fields=[
                'stripe_user_id',
                'updated_at'
            ])

            request.session['notification'] = 'is_just_stripe_authorization_complete'

        return redirect('profile')