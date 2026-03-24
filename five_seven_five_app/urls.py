from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = "five_seven_five_app"

urlpatterns = [
    path('', views.index, name='index'),
    path('haiku/<int:haiku_id>/', views.haiku_detail, name='haiku_detail'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('liked/', views.liked_haikus, name='liked'),
    path('following/', views.following_feed, name='following'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('search/', views.search, name='search'),
    path('post/', views.post_haiku, name="post_haiku"),
    path('haiku/<int:haiku_id>/like/', views.toggle_like, name='toggle_like'),
    path('profile/<str:username>/follow/', views.toggle_follow, name='toggle_follow'),
    path('haiku/<int:haiku_id>/comment/', views.add_comment, name='add_comment'),
    path('edit_profile',views.edit_profile, name='edit_profile'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)