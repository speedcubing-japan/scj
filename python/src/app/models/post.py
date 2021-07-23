from django.db import models
from .person import Person
from app.defines.information import Type as InformationType


class Post(models.Model):

    type = models.IntegerField("種類", choices=InformationType.choices())
    title = models.CharField("タイトル", max_length=24)
    text = models.TextField("本文")
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    def __str__(self):
        return self.title
