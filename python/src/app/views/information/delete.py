from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from app.models import Information


class Delete(LoginRequiredMixin, TemplateView):
    def get(self, request, **kwargs):
        if not request.user.is_superuser and not request.user.is_staff:
            return redirect('index')

        id = kwargs.get('id')

        information = Information.objects.filter(id=id)
        if not information.exists():
            return redirect('index')
        information = information.first()

        context = {
            'information': information,
        }

        return render(request, 'app/information/delete.html', context)

    def post(self, request, **kwargs):
        if not request.user.is_superuser and not request.user.is_staff:
            return redirect('index')

        id = kwargs.get('id')

        information = Information.objects.filter(id=id)
        information = information.first()
        if request.user.is_staff and information.person.user.id is not request.user.id:
            return redirect('index')

        Information.objects.filter(id=id).delete()

        request.session['notification'] = 'is_just_information_delete'

        return redirect('post_list')