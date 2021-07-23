from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.views.generic import TemplateView
from app.models import Information
from app.defines.information import TypeEn as InformationTypeEn


class List(TemplateView):
    def get(self, request, **kwargs):
        PAGE_SIZE = 10

        page = self.request.GET.get(key='page', default=1)

        type = kwargs.get('type')
        if type == "":
            return redirect('index')

        if type == 'all':
            all_informations = Information.objects \
                .filter(is_public=True) \
                .order_by('updated_at') \
                .reverse()
        else:
            if not InformationTypeEn.contains_name(type):
                return redirect('index')

            type_id = InformationTypeEn.get_value(type)
            all_informations = Information.objects \
                .filter(type=type_id) \
                .filter(is_public=True) \
                .order_by('updated_at') \
                .reverse()

        pagenator = Paginator(all_informations, PAGE_SIZE)
        informations = pagenator.get_page(page)

        context = {
            'informations': informations,
            'type': type
        }

        return render(request, 'app/information/list.html', context)
