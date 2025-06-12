from django.db import models

# Create your models here.


class Post(models.Model):
    post_title = models.CharField(max_length=50)
    post_content = models.TextField()
    author_name = models.CharField(max_length=50)
    created_date = models.DateField()
