from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


# Create your models here.
class HaikuUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateField()

    def __str__(self):
        return self.user.username

class Profile(models.Model):
    username = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    bio = models.CharField(max_length=100)
    profile_picture = models.ImageField(upload_to=settings.MEDIA_ROOT)

    def __str__(self):
        return str(self.username)

class Haiku(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    haiku = models.CharField(max_length=1000)
    created_at = models.DateField()

    def __str__(self):
        return self.haiku


class Comment(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    haiku = models.ForeignKey(Haiku,  on_delete=models.CASCADE)
    comment_text =  models.CharField(max_length=100)
    created_at = models.DateField()

    def __str__(self):
        return f"{self.username} comment on {self.haiku}: {self.comment_text}"


class Like(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    haiku = models.ForeignKey(Haiku,  on_delete=models.CASCADE)
    created_at = models.DateField()

    def __str__(self):
        return f"{self.username} likes {self.haiku}"


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following" )
    following = models.ForeignKey(User, on_delete=models.CASCADE,related_name="followed_by" )
    created_at = models.DateField()

    def __str__(self):
        return f"{self.follower} follows {self.following}"
