from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from app.models import Post
from app.forms import PostEditForm
from app.defines.information import TypeEn as InformationTypeEn
from app.defines.session import Notification


class Edit(LoginRequiredMixin, TemplateView):
    def get(self, request, **kwargs):
        if (
            request.user.person.is_community_posting_offer
            or not request.user.is_superuser
        ):
            return redirect("index")

        id = kwargs.get("id")

        post = Post.objects.filter(id=id)
        if not post.exists():
            return redirect("index")
        post = post.first()
        form = PostEditForm(initial={"title": post.title, "text": post.text})

        context = {"form": form, "post": post, "notification": ""}

        return render(request, "app/post/edit.html", context)

    def post(self, request, **kwargs):
        if (
            request.user.person.is_community_posting_offer
            or not request.user.is_superuser
        ):
            return redirect("index")

        post_form = PostEditForm(request.POST)
        id = kwargs.get("id")

        if post_form.is_valid():
            post = Post.objects.filter(id=id)
            if not post.exists():
                return redirect("index")

            post = post.first()
            post.type = InformationTypeEn.event.value
            post.title = post_form.cleaned_data["title"]
            post.text = post_form.cleaned_data["text"]
            post.save(update_fields=["type", "title", "text", "updated_at"])

            form = PostEditForm(initial={"title": post.title, "text": post.text})

            context = {"form": form, "post": post, "notification": Notification.UPDATE}

            return render(request, "app/post/edit.html", context)
