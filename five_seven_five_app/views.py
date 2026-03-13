from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .forms import UserForm, ProfileForm
import datetime
# Create your views here.

from .models import Haiku, Profile, Comment, Like, Follow


def index(request):
    haikus = Haiku.objects.all().order_by('-created_at')
    profiles = [Profile.objects.get(username = haiku.username) for haiku in haikus]
    return render(request, 'index.html', {'haikus': haikus, 'profiles':profiles})


def haiku_detail(request, haiku_id):
    haiku = get_object_or_404(Haiku, id=haiku_id)
    comments = Comment.objects.filter(haiku=haiku)

    return render(request, 'haiku_detail.html', {
        'haiku': haiku,
        'comments': comments
    })


def profile(request, username):
    user = get_object_or_404(Profile, username__username=username)

    haikus = Haiku.objects.filter(username=user)

    profile = Profile.objects.get(username=user)

    
    profiles = [Profile.objects.get(username = haiku.username) for haiku in haikus]

    return render(request, 'profile.html', {
        'profile': profile,
        'haikus': haikus,
        'profiles':profiles

    })


def liked_haikus(request):
    if not request.user.is_authenticated:
        return render(request, 'login_required.html')

    user = Profile.objects.get(user=request.user)

    liked = Like.objects.filter(username=user)

    haikus = [like.haiku for like in liked]

    return render(request, 'liked.html', {'haikus': haikus})


def following_feed(request):
    if not request.user.is_authenticated:
        return render(request, 'login_required.html')

    user = Profile.objects.get(user=request.user)

    following = Follow.objects.filter(follower=user)

    users = [f.following for f in following]

    haikus = Haiku.objects.filter(username__in=users)

    return render(request, 'following.html', {'haikus': haikus})

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
