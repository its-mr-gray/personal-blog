from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class Post(models.Model):
    post_title = models.CharField(max_length=50)
    post_content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_date = models.DateField()
