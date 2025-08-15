from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ArtistViewSet, AlbumViewSet, ReviewViewSet
from .views import spotify_callback, spotify_connect, spotify_refresh, spotify_search
from .views import spotify_album_details, spotify_new_releases, get_combined_album_details, get_artist_albums

router = DefaultRouter()
router.register(r'artists', ArtistViewSet)
router.register(r'albums', AlbumViewSet)
router.register(r'reviews', ReviewViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path("spotify/callback/", spotify_callback, name="spotify-callback"),
    path("spotify/refresh/", spotify_refresh, name="spotify-refresh"),
    path("spotify/connect/", spotify_connect, name="spotify-connect"),
    path("spotify/search/", spotify_search, name="spotify-search"),
    path("spotify/albums/<str:spotify_id>/", spotify_album_details, name="spotify-album-details"),
    path("spotify/browse/new-releases/", spotify_new_releases, name="spotify-new-releases"),
    path("album-details/<str:spotify_id>/", get_combined_album_details, name="combined-album-details"),
    path("spotify/artists/<str:artist_id>/albums/", get_artist_albums, name="spotify-artist-albums"),
]
