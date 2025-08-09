from django.db import models
from django.contrib.auth.models import User

class Artist(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Album(models.Model):
    title = models.CharField(max_length=200)
    artist = models.ForeignKey(Artist, related_name='albums', on_delete=models.CASCADE)
    release_year = models.PositiveIntegerField()
    genre = models.CharField(max_length=100)

    def __str__(self):
        return self.title

class Review(models.Model):
    album = models.ForeignKey(Album, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()  # e.g., 1-5
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review of {self.album} by {self.user}'
