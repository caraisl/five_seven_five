from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class HaikuUser(models.Model):
    user = models.OneToOneField(User)
    created_at = models.DateField()

    def __str__(self):
        return self.user.username

class Profile(models.Model):
    username = models.OneToOneField(HaikuUser, on_delete=models.CASCADE, primary_key=True)
    bio = models.CharField(max_length=100)
    profile_picture = models.ImageField()

    def __str__(self):
        return self.username

class Haiku(models.Model):
    username = models.ForeignKey(HaikuUser)
    haiku = models.CharField(max_length=1000)
    created_at = models.DateField()

    def __str__(self):
        return self.haiku


class Comment(models.Model):
    username = models.ForeignKey(HaikuUser)
    haiku = models.ForeignKey(Haiku)
    comment_text =  models.CharField(max_length=100)
    created_at = models.DateField()

    def __str__(self):
        return f"{self.username} comment on {self.haiku}: {self.comment_text}"


class Like(models.Model):
    username = models.ForeignKey(HaikuUser)
    haiku = models.ForeignKey(Haiku)
    created_at = models.DateField()

    def __str__(self):
        return f"{self.username} likes {self.haiku}"


class Follow(models.Model):
    follower = models.ForeignKey(HaikuUser)
    following = models.ForeignKey(HaikuUser)
    created_at = models.DateField()

    def __str__(self):
        return f"{self.follower} follows {self.following}"
