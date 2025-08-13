from rest_framework import viewsets, permissions, filters
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core import signing
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response

from django.db.models import Avg, Count, FloatField, IntegerField
from django.db.models.functions import Coalesce

from .models import Artist, Album, Review
from .serializers import ArtistSerializer, AlbumSerializer, ReviewSerializer
from .permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly

from django.shortcuts import redirect
from django.http import JsonResponse
from .spotify import get_spotify_auth_url, get_tokens
from .spotify import build_auth_url, exchange_code_for_token, tokens_response_to_saved_fields, refresh_access_token, make_spotify_request
from .models import SpotifyToken


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

    def get_queryset(self):
        return Album.objects.annotate(
        avg_rating=Avg('reviews__rating', output_field=FloatField()),
        review_count=Count('reviews', output_field=IntegerField())
    )

    @action(detail=False, methods=['get'])
    def top_rated(self, request):
        # Annotate avg_rating on queryset to use in ordering
        top_albums = self.get_queryset().order_by('-avg_rating')[:10]
        serializer = self.get_serializer(top_albums, many=True)
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsOwnerOrReadOnly]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['album__title', 'rating', 'user__username']  # Filter by album, rating, user
    search_fields = ['album__title', 'comment', 'user__username']  # Search in comment, album title, or username
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']  # Default ordering

    # a user can see their own set of reviews
    def get_queryset(self):
        """
        If a 'user' query param is set to 'me', filter reviews
        for the currently authenticated user.
        """
        queryset = Review.objects.all().order_by('-created_at') # Add default ordering here
        user_filter = self.request.query_params.get('user')
        
        if user_filter == 'me' and self.request.user.is_authenticated:
            queryset = queryset.filter(user=self.request.user)
            
        return queryset
    
SIGNING_SALT = "spotify-auth-salt"  # change to project-unique string


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def spotify_connect(request):
    """
    Protected endpoint: starts the Spotify OAuth flow for the logged-in user.
    Returns a redirect to Spotify's auth page.
    Uses signed 'state' to associate the callback with this user.
    """
    user = request.user
    # create signed state with user_id and timestamp
    state_payload = {"user_id": user.id, "ts": timezone.now().timestamp()}
    state = signing.dumps(state_payload, salt=SIGNING_SALT)

    auth_url = build_auth_url(state)
    # redirect user to Spotify's login URL
    return redirect(auth_url)


@api_view(["GET"])
@permission_classes([AllowAny])  # Spotify will call this endpoint, so allow public
def spotify_callback(request):
    """
    Handle Spotify redirect. Spotify will include 'code' and 'state'.
    We validate state, exchange code for tokens, and save them to the DB for the user.
    """
    error = request.GET.get("error")
    if error:
        return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

    code = request.GET.get("code")
    state = request.GET.get("state")
    if not code or not state:
        return Response({"error": "Missing code or state"}, status=status.HTTP_400_BAD_REQUEST)

    # validate state
    try:
        state_payload = signing.loads(state, salt=SIGNING_SALT, max_age=300)  # optional max_age sec
        user_id = state_payload.get("user_id")
    except signing.BadSignature:
        return Response({"error": "Invalid state"}, status=status.HTTP_400_BAD_REQUEST)
    except signing.SignatureExpired:
        return Response({"error": "State expired"}, status=status.HTTP_400_BAD_REQUEST)

    # exchange code for tokens
    try:
        token_json = exchange_code_for_token(code)
    except Exception as exc:
        # log error or return readable message
        return Response({"error": "Token exchange failed", "details": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    fields = tokens_response_to_saved_fields(token_json)

    # save tokens to DB for the user
    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST)

    spotify_obj, created = SpotifyToken.objects.get_or_create(user=user)
    spotify_obj.access_token = fields["access_token"]
    # only update refresh_token if present (Spotify may omit on refresh)
    if fields.get("refresh_token"):
        spotify_obj.refresh_token = fields["refresh_token"]
    spotify_obj.scope = fields["scope"]
    spotify_obj.token_type = fields["token_type"]
    spotify_obj.expires_at = fields["expires_at"]
    spotify_obj.save()

    # For development, return JSON. In production you may redirect to frontend.
    return Response({
        "detail": "Spotify connected",
        "user": user.username,
        "created": created,
        "expires_at": spotify_obj.expires_at,
    }, status=status.HTTP_200_OK)


# Optional helper view: force-refresh Spotify access token for authenticated user
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def spotify_refresh(request):
    user = request.user
    try:
        token_obj = user.spotify_token
    except SpotifyToken.DoesNotExist:
        return Response({"error": "No Spotify tokens for user"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        token_resp = refresh_access_token(token_obj.refresh_token)
    except Exception as exc:
        return Response({"error": "Refresh failed", "details": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    # update saved fields (note: response may omit refresh_token)
    fields = tokens_response_to_saved_fields(token_resp)
    token_obj.access_token = fields["access_token"] or token_obj.access_token
    if fields.get("refresh_token"):
        token_obj.refresh_token = fields["refresh_token"]
    token_obj.token_type = fields.get("token_type", token_obj.token_type)
    token_obj.scope = fields.get("scope", token_obj.scope)
    token_obj.expires_at = fields.get("expires_at", token_obj.expires_at)
    token_obj.save()

    return Response({"detail": "Spotify token refreshed", "expires_at": token_obj.expires_at})

# search spotify albums
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def spotify_search(request):
    query = request.GET.get("q")
    # Get the search type from the request, default to 'artist'
    search_type = request.GET.get("type", "artist") 

    if not query:
        return Response({"error": "Query parameter 'q' is required."}, status=400)
    
    endpoint = f"/v1/search?q={query}&type={search_type}&limit=10"
    try:
        results = make_spotify_request(request.user, endpoint)
        # The key in the response will change based on the type
        # e.g., 'artists' or 'albums'
        return Response(results)
    except Exception as e:
        return Response({"error": str(e)}, status=500)
    
# get spotify album details
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def spotify_album_details(request, spotify_id):
    """
    Gets detailed information for a single Spotify album.
    """
    endpoint = f"/v1/albums/{spotify_id}"
    try:
        results = make_spotify_request(request.user, endpoint)
        return Response(results)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

# browse new spotify releases
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def spotify_new_releases(request):
    """
    Gets a list of new album releases from Spotify.
    """
    # The endpoint for new releases in Spotify API
    endpoint = "/v1/browse/new-releases?limit=20"
    try:
        results = make_spotify_request(request.user, endpoint)
        return Response(results.get("albums", {}).get("items", []))
    except Exception as e:
        return Response({"error": str(e)}, status=500)
    
# get the album data from spotify and the api album data
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_combined_album_details(request, spotify_id):
    """
    Fetches album details from Spotify and combines them with
    local reviews from this application's database.
    """
    try:
        # 1. Fetch album metadata from Spotify
        spotify_data = make_spotify_request(request.user, f"/v1/albums/{spotify_id}")

        # 2. Fetch local reviews for this album
        local_reviews = Review.objects.filter(album__spotify_id=spotify_id)
        review_serializer = ReviewSerializer(local_reviews, many=True)

        # 3. Combine the data into a single response
        combined_data = {
            "spotify_details": spotify_data,
            "local_reviews": review_serializer.data
        }
        return Response(combined_data)

    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_artist_albums(request, artist_id):
    """
    Gets a list of albums for a specific artist from Spotify.
    """
    endpoint = f"/v1/artists/{artist_id}/albums"
    try:
        results = make_spotify_request(request.user, endpoint)
        # We return the 'items' array from the Spotify response
        return Response(results.get("items", []))
    except Exception as e:
        return Response({"error": str(e)}, status=500)