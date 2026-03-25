from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

import syllables

from .models import Profile, Haiku


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class ProfileForm(forms.ModelForm):
    bio = forms.CharField(
        widget=forms.Textarea(attrs={'style': "display:block;"}),
        required=False
    )
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = Profile
        fields = ('bio', 'profile_picture')


class HaikuForm(forms.ModelForm):
    haiku = forms.CharField(widget=forms.Textarea(attrs={'style': "display:block;"}))

    class Meta:
        model = Haiku
        fields = ('haiku', 'haiku_picture')

    def clean_haiku(self):
        value = self.cleaned_data["haiku"]
        if not validate_haiku(value):
            raise ValidationError(
                "Not a haiku. Please check your syllables.",
                code="invalid",
            )
        return value


def validate_haiku(haiku):
    syllable_count = [syllables.estimate(line) for line in haiku.split("\n")]
    return syllable_count == [5, 7, 5]