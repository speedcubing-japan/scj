from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from app.defines.information import Type as InformationType
from app.defines.information import TypeEn as InformationTypeEn
from app.forms import PostForm, InformationForm
from .util import make_post_text


class Confirm(LoginRequiredMixin, TemplateView):
    def get(self, request):
        session_form_data = request.session.get('post_form_data')
        session_form_data_format = request.session.get('post_form_data_format')

        if not session_form_data or not session_form_data_format:
            return redirect('index')

        format = session_form_data_format

        if format == 'event':
            form = PostForm(session_form_data)
            type = InformationTypeEn.event.value
            text = make_post_text(form.data)
        elif format == 'information':
            form = InformationForm(session_form_data)
            type = form.data['type']
            text = form.data['text']

        type_display_name = InformationType.get_name(int(type))

        context = {
            'form': form,
            'text': text,
            'type_display_name': type_display_name,
            'format': format
        }

        return render(request, 'app/post/confirm.html', context)
