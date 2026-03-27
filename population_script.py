import os
from datetime import datetime
os.environ.setdefault('DJANGO_SETTINGS_MODULE','five_seven_five.settings')

import django
django.setup()
from django.core.files import File 

from five_seven_five_app.models import Haiku, Profile, Comment, Like, Follow, User

def populate():
    users = [
        {"username": "haikuUser1",          "password":"12345", "created":datetime(1967,12,30)},
        {"username": "haikuUser2",          "password":"12345", "created":datetime(2011,11,11)},
        {"username": "haikuLover222",       "password":"12345", "created":datetime(2023,12,25)},
        {"username": "Dave67",              "password":"12345", "created":datetime(1967,12,30)},
        {"username": "IheartHaikus",        "password":"12345", "created":datetime(2006,5,29)},
        {"username": "myFlatmateHolly",     "password":"12345", "created":datetime(2005,7,7)},
        {"username": "haikuHater666",       "password":"12345", "created":datetime(1967,12,30)},
        {"username": "xxep1cF4res123xx",    "password":"12345", "created":datetime(1886,12,30)},
        {"username": "StanielTheAntiFares", "password":"12345", "created": datetime(1994,4,1)},
    ]

    haikus = [
        {"username":"haikuUser1", "haiku": "Here's five syllables,\nHere is seven syllables,\nHere is five again", },
        {"username":"Dave67", "haiku": "one two three four five,\nseven has two syllables,\none two three four five", },
        {"username":"IheartHaikus", "haiku": "I don't like Haikus,\npetition to ban haikus,\nthey make me feel sad ", },
        {"username":"IheartHaikus", "haiku": "I've changed my mind now,\nHaikus are extremely cool,\nthey bring me such joy ", },
        {"username":"myFlatmateHolly",
         "haiku": "I can do Haiku,\nbetter than you can do it,\nwatch me do it now", 
         "likes":["haikuUser1", "haikuUser2"] ,
         "comments":{"haikuUser1":"very nice Haiku Holly"}},
        {"username":"haikuHater666", "haiku": "boo boo boo boo boo,\nI hate Haikus so so much \n, this haiku site sucks",},
        {"username":"xxep1cF4res123xx", 'haiku': "Stanley speaks once more,\ndiction dry like the desert,\nmust i endure more"},
        {"username":"StanielTheAntiFares","haiku":"He crashes servers,\nFares does cyberwarfare,\nHe shouldn't do that"},
        {"username":"xxep1cF4res123xx", 'haiku': "It takes bravery\nto write something so dreadful\nand to then hit send", "comments":{'xxep1cF4res123xx':"This one's for you stanley."}}
    ]

    follows = {"StanielTheAntiFares":["xxep1cF4res123xx", "myFlatmateHolly", "haikuHater666"], "myFlatmateHolly": ["IheartHaikus","Dave67"]}
    
    for user in users:
        print(user)
        newUser, created = User.objects.get_or_create(username=user['username'])
        print(created)
        newUser.set_password(user['password'])
        newUser.save()
        print(Profile.objects.filter(username = newUser).count())

        if Profile.objects.filter(username = newUser).count() == 0:
            print(os.path.join("populate_pics", user.get('profile_pic','default.png')))
            with open(os.path.join("populate_pics", user.get('profile_pic','default.png')), 'rb') as f:
                profile_pic = File(f)
                newProfile = Profile.objects.get_or_create(username=newUser, profile_picture =  profile_pic, bio = user.get('bio', 'I like Haikus'), created_at = user['created'])[0]
                newProfile.save()

        

    for haiku in haikus:
        print(haiku)
        print(Profile.objects.all())
        newHaiku = Haiku.objects.get_or_create(username=Profile.objects.get(username__username=haiku['username']), haiku=haiku['haiku'], created_at = haiku.get('created', datetime.now()))[0]
        newHaiku.save()
        for comment in haiku.get("comments", []):
            haikuComment = Comment.objects.get_or_create(username=User.objects.get(username=comment), haiku=newHaiku, comment_text = haiku['comments'][comment], created_at = datetime.now())[0]
            haikuComment.save()
        for like in haiku.get('likes', []):
            newLike = Like.objects.get_or_create(username=User.objects.get(username = like), haiku= newHaiku, created_at=datetime.now())[0]
            newLike.save()
    
    for follower in follows:
        for following in follows[follower]:
            newFollow = Follow.objects.get_or_create(follower=User.objects.get(username=follower),following=User.objects.get(username=following), created_at= datetime.now())[0]
            newFollow.save()

if __name__ == '__main__':
    print("Starting five_seven_five population script...")
    populate()
        







