from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from app.models import Post, Information


class List(LoginRequiredMixin, TemplateView):
    def get(self, request):
        if not request.user.person.is_community_posting_offer and not request.user.is_superuser and not request.user.is_staff:
            return redirect('index')

        posts = []
        if request.user.person.is_community_posting_offer:
            posts = Post.objects \
                .filter(person__id=request.user.person.id) \
                .order_by('created_at') \
                .reverse()
            informations = Information.objects \
                .filter(person__id=request.user.person.id) \
                .order_by('created_at') \
                .reverse()

        if request.user.is_superuser:
            posts = Post.objects.order_by('updated_at').reverse().all()
            informations = Information.objects.order_by('updated_at').reverse().all()

        if request.user.is_staff:
            informations = Information.objects \
                .filter(person__id=request.user.person.id) \
                .order_by('created_at') \
                .reverse()

        close_informations = []
        open_informations = []
        for information in informations:
            if information.is_public:
                open_informations.append(information)
            else:
                close_informations.append(information)

        notification = self.request.session.get('notification')
        if self.request.session.get('notification') is not None:
            del self.request.session['notification']

        context = {
            'posts': posts,
            'close_informations': close_informations,
            'open_informations': open_informations,
            'notification': notification,
        }

        return render(request, 'app/post/list.html', context)