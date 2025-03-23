from django.db import models
from django.contrib.auth.models import User

# Categories Model
class Category(models.Model):
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=6)

    def __str__(self):
        return self.name

# Tags Model
class Tag(models.Model):
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=6) 

    def __str__(self):
        return self.name

# Books Model
class Book(models.Model):
    STATUS_CHOICES = [
        ('unread', 'Unread'),
        ('reading', 'Reading'),
        ('finished', 'Finished'),
        ('wont_finish', "Won't Finish"),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    authors = models.CharField(max_length=255)
    cover_image = models.URLField()
    pages = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unread')
    rating = models.FloatField()
    favourite = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    categories = models.ManyToManyField(Category)

    def __str__(self):
        return self.title

# Notemarks Model
class Notemark(models.Model):
    title = models.CharField(max_length=255)
    chapter = models.CharField(max_length=255)
    page = models.IntegerField()
    color = models.CharField(max_length=6)
    favourite = models.BooleanField(default=False)
    tag = models.ForeignKey(Tag, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title
