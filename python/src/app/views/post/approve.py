from django.shortcuts import redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from app.models import Post, Information


class Approve(LoginRequiredMixin, View):
    def get(self, request, **kwargs):
        if request.user.person.is_community_posting_offer or not request.user.is_superuser:
            return redirect('index')

        id = kwargs.get('id')

        post = Post.objects.filter(id=id)
        if not post.exists():
            return redirect('index')
        post = post.first()

        information = Information(
            type=post.type,
            title=post.title,
            text=post.text,
            is_public=False
        )
        information.person = request.user.person
        information.save()
        # 削除
        Post.objects.filter(id=id).delete()

        request.session['notification'] = 'is_just_post_approve'

        return redirect('post_list')