from rest_framework import viewsets, permissions, filters
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend

from .models import Artist, Album, Review
from .serializers import ArtistSerializer, AlbumSerializer, ReviewSerializer
from .permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly


class ArtistViewSet(viewsets.ModelViewSet):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['name']  # Exact match filtering
    search_fields = ['name']     # Search by artist name
    ordering_fields = ['name']
    ordering = ['name']  # Default ordering


class AlbumViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    permission_classes = [IsAdminOrReadOnly]

    parser_classes = (MultiPartParser, FormParser)  # Handle image uploads

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['artist__name', 'release_year']  # Filtering by artist name or release year
    search_fields = ['title', 'artist__name']  # Search album title or artist name
    ordering_fields = ['release_year', 'title']
    ordering = ['title']  # Default ordering


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsOwnerOrReadOnly]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['album__title', 'rating', 'user__username']  # Filter by album, rating, user
    search_fields = ['album__title', 'comment', 'user__username']  # Search in comment, album title, or username
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']  # Default ordering

    def perform_create(self, serializer):
        # Automatically assign logged-in user as review author
        serializer.save(user=self.request.user)
