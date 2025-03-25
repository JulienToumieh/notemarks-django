import os
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Function to generate dynamic filename for cover image
def upload_cover_image(instance, filename):
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    ext = filename.split('.')[-1]
    return f'cover_image_{timestamp}.{ext}'

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
    description = models.TextField(blank=True)
    authors = models.CharField(max_length=255)
    cover_image = models.CharField(max_length=255, blank=True, null=True)  # Use CharField for just a string
    pages = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unread', blank=True)
    rating = models.FloatField(blank=True, null=True)
    favourite = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    categories = models.ManyToManyField(Category)
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return self.title



# Notemarks Model
class Notemark(models.Model):
    title = models.CharField(max_length=255)
    chapter = models.CharField(max_length=255)
    page = models.IntegerField()
    color = models.CharField(max_length=6)
    favourite = models.BooleanField(default=False)
    tags = models.ManyToManyField(Tag, blank=True)  # Many-to-many relationship for tags

    def __str__(self):
        return self.title
