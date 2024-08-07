from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from app.forms import PostForm, InformationForm
from app.models import Information
from app.defines.session import Notification


class Input(LoginRequiredMixin, TemplateView):
    def get(self, request, **kwargs):
        if (
            not request.user.person.is_community_posting_offer
            and not request.user.is_superuser
            and not request.user.is_staff
        ):
            return redirect("index")

        format = kwargs.get("format")
        if not format:
            return redirect("index")

        if format == "event":
            form = PostForm()
        elif format == "information":
            form = InformationForm()
            if request.user.is_staff:
                form.fields["is_public"].widget.attrs["disabled"] = "disabled"
        else:
            return redirect("index")

        context = {"form": form, "format": format}
        return render(request, "app/post/input.html", context)

    def post(self, request, **kwargs):
        format = kwargs.get("format")

        if not format:
            return redirect("index")

        if format == "event":
            form = PostForm(request.POST)
        elif format == "information":
            form = InformationForm(request.POST)
        else:
            return redirect("index")

        if form.is_valid():
            if format == "event":
                request.session["post_form_data"] = request.POST
                request.session["post_form_data_format"] = format
                return redirect("post_confirm")
            elif format == "information":
                type = form.cleaned_data["type"]
                text = form.cleaned_data["text"]

                if request.user.is_superuser:
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
                else:
                    return redirect("post_input")

                return redirect("post_list")

        context = {
            "form": form,
        }
        return render(request, "app/post/input.html", context)
