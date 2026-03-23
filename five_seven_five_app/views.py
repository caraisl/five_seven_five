from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import UserForm, ProfileForm, HaikuForm
import datetime
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
import syllables
# Create your views here.

from .models import Haiku, Profile, Comment, Like, Follow, User


def index(request):
    haikus = Haiku.objects.all().order_by('-created_at')

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

    return render(request, 'haiku_detail.html', {
        'haiku': haiku,
        'comments': comments
    })


def profile(request, username):
    user = get_object_or_404(Profile, username__username=username)
    profile = Profile.objects.get(username=user)
    haikus = Haiku.objects.filter(username=user)
    context = feed(request, haikus)
    context['profile'] = profile;

    



    return render(request, 'profile.html', context)


def liked_haikus(request):
    if not request.user.is_authenticated:
        return redirect('five_seven_five_app:login')

    user = User.objects.get(username=request.user)

    liked = Like.objects.filter(username=user)

    haikus = [like.haiku for like in liked]
    context = feed(request, haikus)
    

    return render(request, 'liked.html', context)


def following_feed(request):
    if not request.user.is_authenticated:
        return redirect('five_seven_five_app:login')

    user = User.objects.get(username=request.user)

    following = Follow.objects.filter(follower=user)

    users = [f.following for f in following]

    haikus = Haiku.objects.filter(username__username__in=users)
    context = feed(request, haikus)

    return render(request, 'following.html', context)

def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = ProfileForm(data=request.POST, files=request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            # Hashes the password
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.username = user
            # Because the created_at in models.py don't have the auto_now_add attribute set, manually fill here
            profile.created_at = datetime.date.today()
            profile.save()

            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = ProfileForm()

    return render(request, 'register.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'registered': registered
    })

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return redirect('five_seven_five_app:index')
            else:
                return HttpResponse("Your account has been disabled.")
        else:
            return HttpResponse("Invalid login information.")
    
    return render(request, 'login.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('five_seven_five_app:index')

def search(request):
    query = request.GET.get('q', '')
    search_type = request.GET.get('type', 'all') # Default to 'all'
    
    haiku_qs = Haiku.objects.filter(haiku__icontains=query) if query else Haiku.objects.none()
    user_qs = Profile.objects.filter(username__username__icontains=query) if query else Profile.objects.none()

    context_dict = {
        'query': query,
        'search_type': search_type,
        'haiku_count': haiku_qs.count(),
        'user_count': user_qs.count(),
    }

    if search_type == 'haiku':
        # Show only haiku
        context_dict['haiku_results'] = haiku_qs
        context_dict['user_results'] = []
    elif search_type == 'user':
        # View only users
        context_dict['haiku_results'] = []
        context_dict['user_results'] = user_qs
    else:
        # Display the first few (Wireframe concept)
        context_dict['haiku_results'] = haiku_qs[:3]
        context_dict['user_results'] = user_qs[:3]

    return render(request, 'search_results.html', context_dict)

    

@login_required
def add_comment(request, haiku_id):
    haiku = get_object_or_404(Haiku, id=haiku_id)

    if request.method == "POST":
        comment_text = request.POST.get("comment_text")

        if comment_text:
            Comment.objects.create(
                username=request.user,
                haiku=haiku,
                comment_text=comment_text,
                created_at=timezone.now().date()
            )

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