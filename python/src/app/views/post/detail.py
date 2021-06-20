from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from app.models import Post


class Detail(LoginRequiredMixin, TemplateView):
    def get(self, request, **kwargs):
        if not request.user.is_superuser:
            return redirect('index')

        id = kwargs.get('id')

        post = Post.objects.filter(id=id)
        if not post.exists():
            return redirect('index')
        if post.first().person.id != request.user.person.id:
            return redirect('index')

        context = {
            'post': post.first()
        }

        return render(request, 'app/post/detail.html', context)