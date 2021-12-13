from django.db import models
from django.contrib.auth.models import User
from markdownx.models import MarkdownxField
from markdownx.utils import markdown

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/mall/category/{self.slug}/'

    class Meta:
        verbose_name_plural = 'Categories'

class Product(models.Model):
    name = models.CharField(max_length=50)
    price = models.IntegerField()
    content = MarkdownxField()
    product_color = models.CharField(max_length=30, default="")
    product_size = models.CharField(max_length=30, default="")
    author = models.ForeignKey(User, null=True, on_delete=models.CASCADE)

    product_image = models.ImageField(upload_to='mall/images/', blank=True)

    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'[{self.pk}] {self.name} :: {self.author}'
    def get_absolute_url(self):
        return f'/mall/{self.pk}/'
    def get_content_markdown(self):
        return markdown(self.content)
    def get_avatar_url(self):
        if self.author.socialaccount_set.exists():
            return self.author.socialaccount_set.first().get_avatar_url()
        else:
            return 'https://doitdjango.com/avatar/id/471/60b65344b416057c/svg/{self.author.email}'

class Comment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.author}::{self.content}'

    def get_absolute_url(self):
        return f'{self.product.get_absolute_url()}#comment-{self.pk}'

    def get_avatar_url(self):
        if self.author.socialaccount_set.exists():
            return self.author.socialaccount_set.first().get_avatar_url()
        else:
            return 'https://doitdjango.com/avatar/id/471/60b65344b416057c/svg/{self.author.email}'
