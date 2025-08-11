from rest_framework import serializers
from rest_framework.validators import ValidationError, UniqueTogetherValidator
from .models import Artist, Album, Review


class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = ['id', 'name']


class AlbumSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer(read_only=True)
    artist_id = serializers.PrimaryKeyRelatedField(
        queryset=Artist.objects.all(), source='artist', write_only=True)

    cover_image_url = serializers.SerializerMethodField() # read only

    def get_cover_image_url(self, obj): # the absolute path for the url
        request = self.context.get('request')
        if obj.cover_image and request:
            return request.build_absolute_uri(obj.cover_image.url)
        return None

    class Meta:
        model = Album
        fields = ['id', 'title', 'artist', 'artist_id', 'release_year', 'genre', 'cover_image', 'cover_image_url']
        validators = [
            UniqueTogetherValidator(
                queryset=Album.objects.all(),
                fields=['title', 'artist'],
                message="This artist already has an album with this title."
            )
        ]


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    album_id = serializers.PrimaryKeyRelatedField(
        queryset=Album.objects.all(), source='album', write_only=True)

    class Meta:
        model = Review
        fields = ['id', 'album_id', 'user', 'rating', 'comment', 'created_at']

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be an integer between 1 and 5.")
        return value
