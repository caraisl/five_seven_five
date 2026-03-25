from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

import syllables
import cmudict
import string
import re

from .models import Profile, Haiku

syllables_dict = cmudict.dict()
phonemes = cmudict.phones()
vowels = [sound[0] for sound in cmudict.phones() if sound[1][0] == "vowel"]

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
        print(vowels)
        value = self.cleaned_data["haiku"]
        if not validate_haiku(value):
            syllables = count_syllables(value)
            raise ValidationError(
                f"Not a haiku - syllables are {','.join([str(i) for i in syllables])}. Please check your syllables.",
                code="invalid",
            )
        return value


def validate_haiku(haiku):
    syllable_counts = count_syllables(haiku)
    return syllable_counts == [5, 7, 5]


def count_syllables(haiku):
    lines = [line for line in haiku.split("\n")]
    words = [line.split(" ") for line in lines]
    syllable_counts = [0,0,0]
    for i,line in enumerate(words):
        for word in line:
            if syllables_dict.get(re.sub(r'[^A-Za-z\']','',word.lower())) != None:
                for phoneme in syllables_dict.get(word.strip().lower())[0]:
                    if phoneme[:2] in vowels:
                        syllable_counts[i] += 1
            else:
                syllable_counts[i] += syllables.estimate(re.sub(r'[^A-Za-z\']','',word.lower()))
    return syllable_counts
