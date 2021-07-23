from django.views.generic import TemplateView
from app.models import Information
from django.shortcuts import render, redirect


class Detail(TemplateView):
    def get(self, request, **kwargs):
        id = kwargs.get("id")
        if 0 < id:
            information = Information.objects.filter(id=id)
            if not information.exists():
                return redirect("index")

            information = information.first()

            is_writer = False
            if (
                request.user.is_authenticated
                and information.person_id == request.user.person.id
            ):
                is_writer = True

            if not information.is_public and not is_writer:
                return redirect("index")

            context = {
                "information": information,
                "title": information.title,
            }

            return render(request, "app/information/detail.html", context)

        return redirect("index")
