from django.db import models
from django.utils import timezone
from markdownx.models import MarkdownxField
from markdownx.utils import markdown

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=50)
    price = models.IntegerField()
    content = models.TextField()
    product_color = models.CharField(max_length=30, default="")
    product_size = models.CharField(max_length=30, default="")

    product_image = models.ImageField(upload_to='mall/images/', blank=True)

    def __str__(self):
        return f'[{self.pk}] {self.name}'
    def get_absolute_url(self):
        return f'/mall/{self.pk}/'
