from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from .forms import ProfileForm, HaikuForm
import datetime
from datetime import timedelta
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.forms import UserCreationForm
# Create your views here.

from .models import Haiku, Profile, Comment, Like, Follow, User


def index(request):
    one_week_ago = timezone.now().date() - timedelta(days=7)

    haikus = Haiku.objects.filter(
        created_at__gte=one_week_ago
    ).annotate(
        popularity=Count('like', distinct=True)
    ).order_by('-popularity', '-created_at')

    if not haikus.exists():
        haikus = Haiku.objects.annotate(
            popularity=Count('like', distinct=True)
        ).order_by('-popularity', '-created_at')

    context = feed(request, haikus)
    return render(request, 'index.html', context)


def feed(request, haikus):
    context = {}
    for haiku in haikus:
        haiku.like_count = Like.objects.filter(haiku=haiku).count()
        haiku.comment_count = Comment.objects.filter(haiku=haiku).count()
        if request.user.is_authenticated:
            haiku.is_liked = Like.objects.filter(
                haiku=haiku,
                username=request.user
            ).exists()
        else:
            haiku.is_liked = False
    context['haikus'] = haikus
    return context


def haiku_detail(request, haiku_id):
    haiku = get_object_or_404(Haiku, id=haiku_id)
    comments = Comment.objects.filter(haiku=haiku)
    haiku.like_count = Like.objects.filter(haiku=haiku).count()
    haiku.comment_count = Comment.objects.filter(haiku=haiku).count()
    for comment in comments:
        comment.profile = Profile.objects.get(username = comment.username)

    return render(request, 'haiku_detail.html', {
        'haiku': haiku,
        'comments': comments
    })


def profile(request, username):
    profile = get_object_or_404(Profile, username__username=username)
    haikus = Haiku.objects.filter(username=profile)

    follower_count = Follow.objects.filter(following=profile.username).count()

    if request.user.is_authenticated:
        is_following = Follow.objects.filter(
            follower=request.user,
            following=profile.username
        ).exists()
    else:
        is_following = False

    context = feed(request, haikus)
    context['profile'] = profile
    context['follower_count'] = follower_count
    context['is_following'] = is_following

    return render(request, 'profile.html', context)


@login_required
def liked_haikus(request):
    user = User.objects.get(username=request.user)

    liked = Like.objects.filter(username=user)
    haikus = [like.haiku for like in liked]

    context = feed(request, haikus)
    return render(request, 'liked.html', context)


@login_required
def following_feed(request):
    user = User.objects.get(username=request.user)

    following = Follow.objects.filter(follower=user)
    users = [f.following for f in following]

    haikus = Haiku.objects.filter(username__username__in=users).order_by('-created_at')
    context = feed(request, haikus)

    return render(request, 'following.html', context)


def register(request):
    if request.method == 'POST':
        user_form = UserCreationForm(data=request.POST)
        profile_form = ProfileForm(data=request.POST, files=request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()

            profile = Profile.objects.create(
                username=user,
                created_at=datetime.date.today()
            )

            raw_password = user_form.cleaned_data.get('password1')
            authenticated_user = authenticate(
                username=user.username,
                password=raw_password
            )

            if authenticated_user is not None:
                login(request, authenticated_user)

            return redirect('five_seven_five_app:edit_profile')
    else:
        user_form = UserCreationForm()
        profile_form = ProfileForm()

    return render(request, 'register.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })



def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get('next', '')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)

                if next_url:
                    return redirect(next_url)

                return redirect('five_seven_five_app:index')
            else:
                return render(request, 'login.html', {
                    'error': 'Your account has been disabled.',
                    'next': next_url
                })
        else:
            return render(request, 'login.html', {
                'error': 'Incorrect username or password.',
                'next': next_url
            })

    next_url = request.GET.get('next', '')
    return render(request, 'login.html', {'next': next_url})


@login_required
def user_logout(request):
    logout(request)
    return redirect('five_seven_five_app:index')


def search(request):
    query = request.GET.get('q', '')
    search_type = request.GET.get('type', 'all')

    haiku_qs = Haiku.objects.filter(haiku__icontains=query) if query else Haiku.objects.none()
    user_qs = Profile.objects.filter(username__username__icontains=query) if query else Profile.objects.none()

    if search_type == 'haiku':
        haiku_results = haiku_qs
        user_results = []
        haikus = haiku_results
    elif search_type == 'user':
        haiku_results = []
        user_results = user_qs
        haikus = []
    else:
        haiku_results = haiku_qs[:3]
        user_results = user_qs[:3]
        haikus = haiku_results

    context_dict = {
        'query': query,
        'search_type': search_type,
        'haiku_count': haiku_qs.count(),
        'user_count': user_qs.count(),
        'haiku_results': haiku_results,
        'user_results': user_results,
    }

    if haikus:
        context_dict.update(feed(request, haikus))
    else:
        context_dict['haikus'] = []

    return render(request, 'search_results.html', context_dict)


@login_required
def add_comment(request, haiku_id):
    haiku = get_object_or_404(Haiku, id=haiku_id)

    if request.method == "POST":
        comment_text = request.POST.get("comment_text")

        if comment_text:
            comment = Comment.objects.create(
                username=request.user,
                haiku=haiku,
                comment_text=comment_text,
                created_at=timezone.now().date()
            )

            profile = Profile.objects.get(username=request.user)

            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({
                    "success": True,
                    "comment_text": comment.comment_text,
                    "created_at": str(comment.created_at),
                    "username": request.user.username,
                    "profile_picture": profile.profile_picture.url if profile.profile_picture else "",
                    "comment_count": Comment.objects.filter(haiku=haiku).count()
                })

    return redirect('five_seven_five_app:haiku_detail', haiku_id=haiku_id)
    


@login_required
def post_haiku(request):
    user_profile = get_object_or_404(Profile, username=request.user)

    if request.method == 'POST':
        form = HaikuForm(request.POST, request.FILES)
        if form.is_valid():
            haiku = form.save(commit=False)
            haiku.username = user_profile
            haiku.created_at = datetime.date.today()
            haiku.save()
            return redirect('five_seven_five_app:haiku_detail', haiku_id=haiku.id)
    else:
        form = HaikuForm()

    return render(request, 'post_haiku.html', {'form': form})


@login_required
def toggle_like(request, haiku_id):
    if request.method != "POST":
        return HttpResponse(status=400)

    haiku = get_object_or_404(Haiku, id=haiku_id)

    like = Like.objects.filter(username=request.user, haiku=haiku).first()

    if like:
        like.delete()
        liked = False
    else:
        Like.objects.create(
            username=request.user,
            haiku=haiku,
            created_at=timezone.now().date()
        )
        liked = True

    like_count = Like.objects.filter(haiku=haiku).count()

    return JsonResponse({
        "liked": liked,
        "like_count": like_count
    })


@login_required
def edit_profile(request):
    user_profile = get_object_or_404(Profile, username=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            if form.cleaned_data['bio'] != "":
                user_profile.bio = form.cleaned_data['bio']
            if form.cleaned_data['profile_picture'] != None:
                user_profile.profile_picture = form.cleaned_data['profile_picture']

            user_profile.save()
            return redirect('five_seven_five_app:profile', username=user_profile.username.username)
    else:
        form = ProfileForm()

    return render(request, 'edit_profile.html', {'form': form})


@login_required
def toggle_follow(request, username):
    if request.method != "POST":
        return HttpResponse(status=400)

    target_user = get_object_or_404(User, username=username)

    if request.user == target_user:
        return HttpResponse(status=400)

    follow = Follow.objects.filter(
        follower=request.user,
        following=target_user
    ).first()

    if follow:
        follow.delete()
        is_following = False
    else:
        Follow.objects.create(
            follower=request.user,
            following=target_user,
            created_at=timezone.now().date()
        )
        is_following = True

    follower_count = Follow.objects.filter(following=target_user).count()

    return JsonResponse({
        "is_following": is_following,
        "follower_count": follower_count
    })