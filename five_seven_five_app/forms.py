from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re

import syllables
import cmudict

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
        haiku = self.cleaned_data["haiku"]
        if not validate_haiku(haiku):
            syllables = count_syllables(haiku)
            raise ValidationError(
                f"Not a haiku - syllables are {','.join([str(i) for i in syllables])}. Please check your syllables.",
                code="invalid",
            )
        return haiku
    
def validate_haiku(haiku):
    syllable_counts = count_syllables(haiku)
    return syllable_counts == [5, 7, 5]


def count_syllables(haiku):
    lines = [line for line in haiku.split("\n")]
    words = [line.split(" ") for line in lines]
    print(words)
    syllable_counts = [0,0,0]
    for i,line in enumerate(words):
        for word in line:
            cleaned_word = re.sub(r'[^A-Za-z\']','',word.lower())
            print(cleaned_word)
            if syllables_dict.get(cleaned_word) != None:
                for phoneme in syllables_dict.get(cleaned_word)[0]:
                    if phoneme[:2] in vowels:
                        syllable_counts[i] += 1
            elif cleaned_word != "":
                syllable_counts[i] += syllables.estimate(cleaned_word)
    return syllable_counts