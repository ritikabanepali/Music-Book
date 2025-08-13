from rest_framework import serializers
from rest_framework.validators import ValidationError, UniqueTogetherValidator
from .models import Artist, Album, Review
from .spotify import make_spotify_request
from django.db import transaction


class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = ['id', 'name']


class AlbumSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer(read_only=True)
    artist_id = serializers.PrimaryKeyRelatedField(
        queryset=Artist.objects.all(), source='artist', write_only=True)
    cover_image_url = serializers.SerializerMethodField() # read only
    average_rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)


    class Meta:
        model = Album
        fields = ['id', 'title', 'artist', 'artist_id', 'release_year', 'genre',
                   'cover_image', 'cover_image_url', 'average_rating', 'review_count']
        validators = [
            UniqueTogetherValidator(
                queryset=Album.objects.all(),
                fields=['title', 'artist'],
                message="This artist already has an album with this title."
            )
        ]

    def get_cover_image_url(self, obj): # the absolute path for the url
        request = self.context.get('request')
        if obj.cover_image and request:
            return request.build_absolute_uri(obj.cover_image.url)
        return None


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    spotify_album_id = serializers.CharField(write_only=True, max_length=255)
    album = AlbumSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'spotify_album_id', 'album', 'user', 'rating', 'comment', 'created_at']

    @transaction.atomic
    def create(self, validated_data):
        spotify_id = validated_data.pop('spotify_album_id')
        user = self.context['request'].user

        # Try to find the album in your local database
        try:
            album = Album.objects.get(spotify_id=spotify_id)
        except Album.DoesNotExist:
            # If it doesn't exist, fetch its data from Spotify
            try:
                endpoint = f"/v1/albums/{spotify_id}"
                album_data = make_spotify_request(user, endpoint)

                # Find or create the artist based on Spotify data
                artist_name = album_data['artists'][0]['name']
                artist, _ = Artist.objects.get_or_create(name=artist_name)

                # Create the new Album record in your database
                album = Album.objects.create(
                    spotify_id=spotify_id,
                    title=album_data['name'],
                    artist=artist,
                    release_year=int(album_data['release_date'][:4]),
                    genre=album_data['genres'][0] if album_data['genres'] else 'Unknown'
                )
            except Exception as e:
                raise serializers.ValidationError(f"Could not fetch or create album from Spotify: {e}")

        # Create the review and link it to the local album record
        review = Review.objects.create(album=album, user=user, **validated_data)
        return review