from django.test import TestCase

import datetime
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from .forms import validate_haiku
from .models import Follow, Haiku, Like, Profile


class HaikuValidationTests(TestCase):
    @patch('five_seven_five_app.forms.syllables.estimate')
    def test_validate_haiku_returns_true_for_575_pattern(self, mock_estimate):
        mock_estimate.side_effect = [5, 7, 5]
        haiku = 'first line\nsecond line\nthird line'

        self.assertTrue(validate_haiku(haiku))

    @patch('five_seven_five_app.forms.syllables.estimate')
    def test_validate_haiku_returns_false_for_non_575_pattern(self, mock_estimate):
        mock_estimate.side_effect = [4, 7, 5]
        haiku = 'first line\nsecond line\nthird line'

        self.assertFalse(validate_haiku(haiku))


class FiveSevenFiveViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        today = datetime.date.today()

        self.user = User.objects.create_user(
            username='alice',
            email='alice@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='bob',
            email='bob@example.com',
            password='testpass123'
        )

        self.profile = Profile.objects.create(
            username=self.user,
            bio='Alice bio',
            created_at=today
        )
        self.other_profile = Profile.objects.create(
            username=self.other_user,
            bio='Bob bio',
            created_at=today
        )

        self.haiku = Haiku.objects.create(
            username=self.profile,
            haiku='An old silent pond\nA frog jumps into the pond\nSplash silence again',
            created_at=today
        )

    def test_index_page_loads(self):
        response = self.client.get(reverse('five_seven_five_app:index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'An old silent pond')

    def test_profile_page_loads(self):
        response = self.client.get(
            reverse('five_seven_five_app:profile', args=[self.user.username])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)

    def test_post_haiku_requires_login(self):
        response = self.client.get(reverse('five_seven_five_app:post_haiku'))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('five_seven_five_app:login'), response.url)

    def test_logged_in_user_can_like_a_haiku(self):
        self.client.login(username='alice', password='testpass123')
        response = self.client.post(
            reverse('five_seven_five_app:toggle_like', args=[self.haiku.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Like.objects.filter(username=self.user, haiku=self.haiku).exists())
        self.assertEqual(response.json()['liked'], True)
        self.assertEqual(response.json()['like_count'], 1)

    def test_second_like_request_removes_existing_like(self):
        Like.objects.create(
            username=self.user,
            haiku=self.haiku,
            created_at=datetime.date.today()
        )
        self.client.login(username='alice', password='testpass123')

        response = self.client.post(
            reverse('five_seven_five_app:toggle_like', args=[self.haiku.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Like.objects.filter(username=self.user, haiku=self.haiku).exists())
        self.assertEqual(response.json()['liked'], False)
        self.assertEqual(response.json()['like_count'], 0)

    def test_logged_in_user_can_follow_another_user(self):
        self.client.login(username='alice', password='testpass123')

        response = self.client.post(
            reverse('five_seven_five_app:toggle_follow', args=[self.other_user.username])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Follow.objects.filter(follower=self.user, following=self.other_user).exists()
        )
        self.assertEqual(response.json()['is_following'], True)
        self.assertEqual(response.json()['follower_count'], 1)

    def test_user_cannot_follow_themselves(self):
        self.client.login(username='alice', password='testpass123')

        response = self.client.post(
            reverse('five_seven_five_app:toggle_follow', args=[self.user.username])
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(
            Follow.objects.filter(follower=self.user, following=self.user).exists()
        )