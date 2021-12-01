from django.db import models
from markdownx.models import MarkdownxField
from markdownx.utils import markdown

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=50)
    price = models.IntegerField()
    content = MarkdownxField()

    prod_image = models.ImageField()
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'[{self.pk}]{self.name}'
    def get_absolute_url(self):
        return f'/mall/{self.pk}/'
