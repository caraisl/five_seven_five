from django import forms
from django.contrib.auth.models import User
from .models import Profile, Haiku
import datetime

# A form for handling basic User data 
class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password',)

# profile description, profile picture
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('bio', 'profile_picture',)

class HaikuForm(forms.ModelForm):
    class Meta:
        model = Haiku
        fields = ('haiku', 'haiku_picture',)