from django.conf import settings
from django.core.cache import cache
from django.test import TestCase, Client
from django.urls import reverse


from ..models import Group, Post, User


POSTS_URL = reverse('posts:posts')
POST_CREATE_URL = reverse('posts:post_create')
USERNAME = 'auth'
PROFILE_URL = reverse('posts:profile', args=[USERNAME])
SLUG = 'slug'
GROUP_URL = reverse('posts:group_list', args=[SLUG])
FOLLOW_URL = reverse('posts:follow_index')
PROFILE_FOLLOW_URL = reverse('posts:profile_follow', args=[USERNAME])
PROFILE_UNFOLLOW_URL = reverse('posts:profile_unfollow', args=[USERNAME])
LOGIN_POST_URL = reverse(settings.LOGIN_URL)
LOGIN_URL_POST_CREATE = f'{LOGIN_POST_URL}?next={POST_CREATE_URL}'
LOGIN_URL_FOLLOW_URL = f'{LOGIN_POST_URL}?next={FOLLOW_URL}'
LOGIN_URL_PROFILE_FOLLOW_URL = f'{LOGIN_POST_URL}?next={PROFILE_FOLLOW_URL}'
LOGIN_URL_PROFILE_UNFOLLOW_URL = (
    f'{LOGIN_POST_URL}?next={PROFILE_UNFOLLOW_URL}')


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_2 = User.objects.create_user(username='name')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.POST_DETAIL_URL = reverse(
            'posts:post_detail', args=[cls.post.id])
        cls.POST_EDIT_URL = reverse('posts:post_edit', args=[cls.post.id])
        cls.LOGIN_URL_POST_EDIT_URL = (
            f'{LOGIN_POST_URL}?next={cls.POST_EDIT_URL}')
        cls.POST_COMMENT_URL = reverse(
            'posts:add_comment', args=[cls.post.id])
        cls.LOGIN_URL_POST_COMMENT_URL = (
            f'{LOGIN_POST_URL}?next={cls.POST_COMMENT_URL}')
        cls.author = Client()
        cls.author.force_login(cls.user)

    def setUp(self):
        self.guest = Client()
        self.another = Client()
        self.another.force_login(self.user_2)

    def test_posts_urls_exists_at_desired_location_unexist_page_unexists(self):
        """Страницы приложения доступны пользователям,
        страница /unexisting_page/ не существует
        """
        cases = [
            [POSTS_URL, self.guest, 200],
            [GROUP_URL, self.guest, 200],
            [PROFILE_URL, self.guest, 200],
            [self.POST_DETAIL_URL, self.guest, 200],
            ['/unexisting_page/', self.guest, 404],
            [POST_CREATE_URL, self.another, 200],
            [self.POST_EDIT_URL, self.author, 200],
            [POST_CREATE_URL, self.guest, 302],
            [self.POST_EDIT_URL, self.guest, 302],
            [self.POST_EDIT_URL, self.another, 302],
            [self.POST_COMMENT_URL, self.author, 302],
            [self.POST_COMMENT_URL, self.guest, 302],
            [FOLLOW_URL, self.another, 200],
            [FOLLOW_URL, self.guest, 302],
            [PROFILE_FOLLOW_URL, self.another, 302],
            [PROFILE_FOLLOW_URL, self.guest, 302],
            [PROFILE_UNFOLLOW_URL, self.another, 302],
            [PROFILE_UNFOLLOW_URL, self.guest, 302],
        ]
        for address, client, code in cases:
            with self.subTest(address=address, client=client):
                self.assertEqual(client.get(address).status_code, code)

    def test_post_create_edit_url_redirect_anonymous_on_auth_login(self):
        """Страница по адресу /create/, /posts/post_id/edit/, posts/post_id/comment/,
        /follow/, /profile/username/follow/, /profile/username/unfollow/
        перенаправит анонимного пользователя на страницу логина.
        """
        cases = [
            [self.POST_EDIT_URL, self.another, self.POST_DETAIL_URL],
            [POST_CREATE_URL, self.guest, LOGIN_URL_POST_CREATE],
            [self.POST_EDIT_URL, self.guest,
                self.LOGIN_URL_POST_EDIT_URL],
            [self.POST_COMMENT_URL, self.guest,
                self.LOGIN_URL_POST_COMMENT_URL],
            [FOLLOW_URL, self.guest, LOGIN_URL_FOLLOW_URL],
            [PROFILE_FOLLOW_URL, self.guest, LOGIN_URL_PROFILE_FOLLOW_URL],
            [PROFILE_UNFOLLOW_URL, self.guest, LOGIN_URL_PROFILE_UNFOLLOW_URL],
        ]
        for address, client, redirect_url in cases:
            with self.subTest(address=address, client=client):
                self.assertRedirects(
                    client.get(address, follow=True),
                    redirect_url
                )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        cache.clear()
        templates_url_names = {
            POSTS_URL: 'posts/index.html',
            GROUP_URL: 'posts/group_list.html',
            PROFILE_URL: 'posts/profile.html',
            self.POST_DETAIL_URL: 'posts/post_detail.html',
            POST_CREATE_URL: 'posts/create_post.html',
            self.POST_EDIT_URL: 'posts/create_post.html',
            FOLLOW_URL: 'posts/follow.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                self.assertTemplateUsed(
                    self.author.get(address),
                    template
                )
