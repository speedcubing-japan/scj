from django.conf import settings
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from app.forms import ProfileForm
from app.defines.session import Notification


class Profile(LoginRequiredMixin, TemplateView):
    def get(self, request):
        form = ProfileForm(initial={
            'prefecture_id': request.user.person.prefecture_id,
        })

        protocol = 'https' if self.request.is_secure() else 'http'
        current_site = get_current_site(self.request)
        domain = current_site.domain
        redirect_uri = protocol + '://' + domain + '/wca/authorization/?type=profile'

        notification = self.request.session.get('notification')
        if self.request.session.get('notification') is not None:
            del self.request.session['notification']

        context = {
            'form': form,
            'wca_oauth_authorization': settings.WCA_OAUTH_AUTHORIZATION,
            'wca_client_id': settings.WCA_CLIENT_ID,
            'stripe_oauth_authorization': settings.STRIPE_OAUTH_AUTHORIZATION,
            'stripe_client_id': settings.STRIPE_CLIENT_ID,
            'redirect_uri': redirect_uri,
            'notification': notification
        }
        return render(request, 'app/scj/profile.html', context)

    def post(self, request):
        profile_form = ProfileForm(request.POST)

        if profile_form.is_valid():
            prefecture_id = profile_form.cleaned_data['prefecture_id']

            person = request.user.person
            person.prefecture_id = prefecture_id
            person.save(update_fields=[
                'prefecture_id',
                'updated_at'
            ])
            request.session['notification'] = Notification.PROFILE_CHANGE

            return redirect('profile')