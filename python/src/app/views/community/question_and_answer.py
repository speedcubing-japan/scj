from django.views.generic import TemplateView


class QuestionAndAnswer(TemplateView):
    template_name = 'app/community/question_and_answer.html'
