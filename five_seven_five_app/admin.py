from django.contrib import admin
from five_seven_five_app.models import Haiku, HaikuUser, Profile, Comment, Like, Follow

# Register your models here.
admin.site.register(Haiku)
admin.site.register(HaikuUser)
admin.site.register(Profile)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Follow)