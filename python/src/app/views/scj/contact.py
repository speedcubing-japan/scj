import requests
from django.views.generic import FormView
from django.conf import settings
from app.forms import ContactForm
from django.shortcuts import redirect
from app.defines.session import Notification


class Contact(FormView):
    template_name = "app/scj/contact.html"
    form_class = ContactForm

    def get_context_data(self, **kwargs):
        context = super(Contact, self).get_context_data(**kwargs)
        context["recaptcha_public_key"] = settings.RECAPTCHA_PUBLIC_KEY
        return context

    def form_valid(self, form):
        captcha = self.request.POST.get("g-recaptcha-response")
        if captcha:
            auth_url = (
                "https://www.google.com/recaptcha/api/siteverify?secret={}&response={}"
            )
            auth_url = auth_url.format(settings.RECAPTCHA_SECRET_KEY, captcha)
            response = requests.get(auth_url)
            if response.json().get("success"):
                form.send_email()
                self.request.session["notification"] = Notification.CONTACT
                return redirect("index")

        form.add_error(None, "私はロボットではありませんにチェックを入れてください。")
        return self.form_invalid(form)
