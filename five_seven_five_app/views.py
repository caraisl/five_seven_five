from django.shortcuts import render, get_object_or_404
# Create your views here.

from .models import Haiku, HaikuUser, Profile, Comment, Like, Follow


def index(request):
    haikus = Haiku.objects.all().order_by('-created_at')
    return render(request, 'index.html', {'haikus': haikus})


def haiku_detail(request, haiku_id):
    haiku = get_object_or_404(Haiku, id=haiku_id)
    comments = Comment.objects.filter(haiku=haiku)

    return render(request, 'haiku_detail.html', {
        'haiku': haiku,
        'comments': comments
    })


def profile(request, username):
    user = get_object_or_404(HaikuUser, user__username=username)

    haikus = Haiku.objects.filter(username=user)

    profile = Profile.objects.get(username=user)

    return render(request, 'profile.html', {
        'profile': profile,
        'haikus': haikus
    })


def liked_haikus(request):
    if not request.user.is_authenticated:
        return render(request, 'login_required.html')

    user = HaikuUser.objects.get(user=request.user)

    liked = Like.objects.filter(username=user)

    haikus = [like.haiku for like in liked]

    return render(request, 'liked.html', {'haikus': haikus})


def following_feed(request):
    if not request.user.is_authenticated:
        return render(request, 'login_required.html')

    user = HaikuUser.objects.get(user=request.user)

    following = Follow.objects.filter(follower=user)

    users = [f.following for f in following]

    haikus = Haiku.objects.filter(username__in=users)

    return render(request, 'following.html', {'haikus': haikus})


