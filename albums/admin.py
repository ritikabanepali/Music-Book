from django.contrib import admin
from .models import Album, Artist, Review # import your model

admin.site.register(Album)
admin.site.register(Artist)
admin.site.register(Review)

