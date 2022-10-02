from app.models import Person
from copy import deepcopy
from app.defines.prefecture import PrefectureAndOversea
from app.defines.gender import Gender
from .admin_base import AdminBase


class AdminPerson(AdminBase):
    template_name = "app/scj/admin/person.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        person_list = Person.objects.all()
        modified = []
        for person in person_list:
            person_dict = person.__dict__
            new_person = deepcopy(person_dict)
            new_person["gender"] = Gender.get_name(person.gender)
            new_person["prefecture"] = PrefectureAndOversea.get_name(
                person.prefecture_id
            )
            new_person["is_active"] = person.user.is_active
            modified.append(new_person)
        context["modified"] = modified
        notification = self.request.session.get("notification")
        if self.request.session.get("notification") is not None:
            del self.request.session["notification"]
        context["notification"] = notification
        prefecture_list = [x[1] for x in PrefectureAndOversea.choices()]
        context["prefecture_list"] = prefecture_list
        return context
