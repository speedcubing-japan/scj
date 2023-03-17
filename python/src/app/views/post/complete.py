from django.conf import settings
from django.shortcuts import redirect
from django.views.generic import View
from django.core.mail import send_mail
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from app.models import Post, Information
from app.defines.information import TypeEn as InformationTypeEn
from app.forms import PostForm, InformationForm
from .util import make_post_text
from app.defines.session import Notification


class Complete(LoginRequiredMixin, View):
    def post(self, request):
        session_form_data = request.session.get("post_form_data")
        session_form_data_format = request.session.get("post_form_data_format")

        if not session_form_data or not session_form_data_format:
            return redirect("post_input")

        del request.session["post_form_data"]
        del request.session["post_form_data_format"]

        format = session_form_data_format
        if format == "event":
            form = PostForm(session_form_data)
        elif format == "information":
            form = InformationForm(session_form_data)

        if form.is_valid():
            if format == "event":
                type = InformationTypeEn.event.value
                text = make_post_text(form.cleaned_data)
            elif format == "information":
                type = form.cleaned_data["type"]
                text = form.cleaned_data["text"]

            if request.user.person.is_community_posting_offer:
                post = Post(
                    type=type,
                    title=form.cleaned_data["title"],
                    text=text,
                    person=request.user.person,
                )
                post.save()

                current_site = get_current_site(self.request)
                domain = current_site.domain
                context = {
                    "protocol": "https" if self.request.is_secure() else "http",
                    "domain": domain,
                    "post": post,
                }

                subject = render_to_string(
                    "app/mail/post_confirm_subject.txt", context
                ).strip()
                message = render_to_string(
                    "app/mail/post_confirm_message.txt", context
                ).strip()
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [settings.EMAIL_INFO],
                )

                request.session["notification"] = Notification.POST_OFFER
            elif request.user.is_superuser:
                information = Information(
                    type=type,
                    title=form.cleaned_data["title"],
                    text=text,
                    person=request.user.person,
                    is_public=form.cleaned_data["is_public"],
                )
                information.save()
                request.session["notification"] = Notification.POST
            elif request.user.is_staff:
                information = Information(
                    type=type,
                    title=form.cleaned_data["title"],
                    text=text,
                    person=request.user.person,
                    is_public=False,
                )
                information.save()
                request.session["notification"] = Notification.POST

            return redirect("post_list")

        return redirect("post_input")
