from django.db import models
from django.db.models import Avg
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class Artist(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Album(models.Model):
    title = models.CharField(max_length=200)
    artist = models.ForeignKey(Artist, related_name='albums', on_delete=models.CASCADE)
    release_year = models.PositiveIntegerField()
    genre = models.CharField(max_length=100)
    cover_image = models.ImageField(upload_to='album_covers/', null=True, blank=True)
    spotify_id = models.CharField(max_length=255, unique=True, null=True, blank=True)

    class Meta:
        unique_together = ('title', 'artist') 

    def __str__(self):
        return self.title

    def average_rating(self):
        return self.reviews.aggregate(avg=Avg('rating'))['avg'] or 0

class Review(models.Model):
    album = models.ForeignKey(Album, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review of {self.album} by {self.user}'

class SpotifyToken(models.Model):
    user = models.OneToOneField(User, related_name='spotify_token', on_delete=models.CASCADE)
    access_token = models.CharField(max_length=1000)
    refresh_token = models.CharField(max_length=1000)
    scope = models.CharField(max_length=500, blank=True)
    token_type = models.CharField(max_length=50, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)  # when access_token expires

    def is_expired(self):
        if not self.expires_at:
            return True
        return timezone.now() >= self.expires_at

    def __str__(self):
        return f"SpotifyToken({self.user.username})"