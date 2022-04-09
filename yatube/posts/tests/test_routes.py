from django.test import TestCase
from django.urls import reverse

from posts.urls import app_name


SLUG = 'slug'
USERNAME = 'auth'
POST_ID = 1
ROUTE_URL_NAMES = [
    ['posts', [], '/'],
    ['group_list', [SLUG], f'/group/{SLUG}/'],
    ['profile', [USERNAME], f'/profile/{USERNAME}/'],
    ['post_detail', [POST_ID], f'/posts/{POST_ID}/'],
    ['post_create', [], '/create/'],
    ['post_edit', [POST_ID], f'/posts/{POST_ID}/edit/'],
    ['follow_index', [], '/follow/'],
    ['profile_follow', [USERNAME], f'/profile/{USERNAME}/follow/'],
    ['profile_unfollow', [USERNAME], f'/profile/{USERNAME}/unfollow/'],
    ['add_comment', [POST_ID], f'/posts/{POST_ID}/comment/'],
]


class PostsURLTests(TestCase):
    def test_urls_uses_correct_route(self):
        """URL-адрес использует соответствующий маршрут."""
        for route, args_data, address in ROUTE_URL_NAMES:
            with self.subTest(route=route):
                self.assertEqual(
                    reverse(f'{app_name}:{route}', args=args_data), address)
