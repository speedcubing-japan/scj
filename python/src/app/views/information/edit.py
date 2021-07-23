from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from app.models import Information
from app.forms import InformationForm
from app.defines.session import Notification


class Edit(LoginRequiredMixin, TemplateView):
    def get(self, request, **kwargs):
        if not request.user.is_superuser and not request.user.is_staff:
            return redirect('index')

        id = kwargs.get('id')

        information = Information.objects.filter(id=id)
        if not information.exists():
            return redirect('index')
        information = information.first()
        form = InformationForm(initial={
            'type': information.type,
            'title': information.title,
            'text': information.text,
            'is_public': information.is_public
        })

        if request.user.is_staff:
            if information.person.user.id is not request.user.id:
                return redirect('index')
            form.fields['is_public'].widget.attrs['disabled'] = 'disabled'

        context = {
            'form': form,
            'information': information,
            'notification': ''
        }

        return render(request, 'app/information/edit.html', context)

    def post(self, request, **kwargs):
        if not request.user.is_superuser and not request.user.is_staff:
            return redirect('index')

        information_form = InformationForm(request.POST)
        id = kwargs.get('id')

        if information_form.is_valid():
            information = Information.objects.filter(id=id)
            if not information.exists():
                return redirect('index')

            information = information.first()
            information.type = information_form.cleaned_data['type']
            information.title = information_form.cleaned_data['title']
            information.text = information_form.cleaned_data['text']
            information.is_public = information_form.cleaned_data['is_public']
            if request.user.is_staff:
                information.is_public = False

            information.save(update_fields=[
                'type',
                'title',
                'text',
                'is_public',
                'updated_at'
            ])

            form = InformationForm(initial={
                'type': information.type,
                'title': information.title,
                'text': information.text,
                'is_public': information.is_public
            })

            if request.user.is_staff:
                if information.person.user.id is not request.user.id:
                    return redirect('index')
                form.fields['is_public'].widget.attrs['disabled'] = 'disabled'

            context = {
                'form': form,
                'information': information,
                'notification': Notification.UPDATE
            }

            return render(request, 'app/information/edit.html', context)
