import os
import csv
from io import TextIOWrapper, StringIO
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from app.models import Competition
from app.views.competition.util import check_competition


class Create(LoginRequiredMixin, TemplateView):
    def get(self, request, **kwargs):
        if not request.user.is_superuser and not request.user.person.is_judge:
            return redirect('index')

        return render(request, 'app/competition/create.html')

    def post(self, request, **kwargs):
        if not request.user.is_superuser and not request.user.person.is_judge:
            return redirect('index')

        errors = []
        context = {}

        file = request.FILES['file']
        if 'competition.csv' in file.name:
            form_data = TextIOWrapper(file.file, encoding='utf-8')
            reader = csv.DictReader(form_data)
            datas = [row for row in reader]

            if len(datas) != 1:
                errors.append('csvファイルが2行でないです。ヘッダーも含めます。')
            else:
                data = datas[0]
                errors.extend(check_competition(data, 'create'))
        else:
            errors.append('competition.csvファイルではないです。')

        if errors:
            context = {'errors': errors}
            return render(request, 'app/competition/create.html', context)
        else:
            competition = Competition()
            competition.create(data, request.user.person.id)
            return redirect('competition_detail', competition.name_id)