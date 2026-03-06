from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('haiku/<int:haiku_id>/', views.haiku_detail, name='haiku_detail'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('liked/', views.liked_haikus, name='liked'),
    path('following/', views.following_feed, name='following'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)