from django.contrib import admin
from .models import HaikuUser, Profile, Haiku, Comment, Like, Follow

# Register your models here.

admin.site.register(HaikuUser)
admin.site.register(Profile)
admin.site.register(Haiku)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Follow)


