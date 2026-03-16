from django.db import models
from django.core.validators import MaxLengthValidator
from django.core.exceptions import ValidationError
import datetime

def validate_isbn(value):
    if not value.isdigit() or len(value) != 13:
        raise ValidationError(
            'ISBN должен содержать ровно 13 цифр'
        )
    

class Book(models.Model):

    title = models.CharField(
        max_length=200,
        validators=[MaxLengthValidator(200)]
    )

    isbn = models.CharField(
        max_length=13,
        validators=[validate_isbn]
    )

    publication_year = models.IntegerField()

    def clean(self):
        if self.publication_year > datetime.date.today().year:
            raise ValidationError({
                'publication_year': 'Год публикации не может быть в будущем'
            })

    def __str__(self):
        return self.title