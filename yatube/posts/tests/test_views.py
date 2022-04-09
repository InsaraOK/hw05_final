import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post, User, Comment, Follow

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


POSTS_URL = reverse('posts:posts')
POSTS_URL_PAGE_2 = f'{POSTS_URL}?page=2'
POST_CREATE_URL = reverse('posts:post_create')
USERNAME = 'auth'
PROFILE_URL = reverse('posts:profile', args=[USERNAME])
USERNAME_2 = 'name'
PROFILE_URL_2 = reverse('posts:profile', args=[USERNAME_2])
SLUG = 'slug'
GROUP_URL = reverse('posts:group_list', args=[SLUG])
SLUG_2 = 'slug_3'
GROUP_URL_2 = reverse('posts:group_list', args=[SLUG_2])
FOLLOW_URL = reverse('posts:follow_index')
POST_NUMBER = settings.POST_NUMBER_ON_PAGE + 1
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
UPLOADED = SimpleUploadedFile(
    name='small.gif',
    content=SMALL_GIF,
    content_type='image/gif'
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.user_2 = User.objects.create_user(username='auth2')
        cls.user_3 = User.objects.create_user(username='auth3')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug',
            description='Тестовое описание',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='slug_2',
            description='Тестовое описание 2',
        )
        cls.GROUP_2_URL = reverse(
            'posts:group_list', args=[cls.group_2.slug])
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=UPLOADED
        )
        Follow.objects.create(
            user=cls.user_2,
            author=cls.user,
        )
        cls.POST_DETAIL_URL = reverse(
            'posts:post_detail', args=[cls.post.id])
        cls.POST_EDIT_URL = reverse('posts:post_edit', args=[cls.post.id])
        cls.author = Client()
        cls.author.force_login(cls.user)
        cls.guest = Client()
        cls.another = Client()
        cls.another.force_login(cls.user_2)
        cls.another_2 = Client()
        cls.another_2.force_login(cls.user_3)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_posts_show_correct_context(self):
        """Шаблоны posts сформированы с правильным контекстом."""
        cache.clear()
        addresses = [
            [GROUP_URL, self.guest],
            [POSTS_URL, self.guest],
            [PROFILE_URL, self.guest],
            [self.POST_DETAIL_URL, self.guest],
            [FOLLOW_URL, self.another],
        ]
        for address, client in addresses:
            with self.subTest(address=address, client=client):
                response = client.get(address)
                if address != self.POST_DETAIL_URL:
                    self.assertEqual(len(response.context['page_obj']), 1)
                    post = response.context['page_obj'][0]
                else:
                    post = response.context['post']
                self.assertEqual(post.author, self.user)
                self.assertEqual(post.text, self.post.text)
                self.assertEqual(post.group, self.group)
                self.assertEqual(post.image, self.post.image)
                self.assertEqual(post.id, self.post.id)

    def test_post_at_incorrect_list(self):
        """Пост не поппал в несоответствующую ленту."""
        cases = [
            [self.GROUP_2_URL, self.another],
            [FOLLOW_URL, self.another_2],
        ]
        for address, client in cases:
            with self.subTest(address=address):
                response = self.another.get(self.GROUP_2_URL)
                self.assertNotIn(self.post, response.context['page_obj'])

    def test_list_group(self):
        """Проверка содержания групп-ленты"""
        response = self.another.get(self.GROUP_2_URL)
        group_context = response.context['group']
        self.assertEqual(group_context, self.group_2)
        self.assertEqual(group_context.title, self.group_2.title)
        self.assertEqual(group_context.slug, self.group_2.slug)
        self.assertEqual(
            group_context.description, self.group_2.description)

    def test_author_profile(self):
        """Проверка авторства страницы профиля"""
        response = self.another.get(PROFILE_URL)
        self.assertEqual(response.context['author'], self.user)

    def test_index_post_list_cache(self):
        """Главная страница кеширует список постов"""
        response = self.guest.get(POSTS_URL)
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.filter(id=self.post.id)[0]
        post.delete()
        self.assertEqual(Post.objects.count(), 0)
        self.assertEqual(
            self.guest.get(POSTS_URL).content, response.content)
        cache.clear()
        self.assertNotEqual(
            self.guest.get(POSTS_URL).content, response.content)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='name')
        cls.PROFILE_URL_PAGE_2 = f'{PROFILE_URL_2}?page=2'
        cls.FOLLOW_URL_PAGE_2 = f'{FOLLOW_URL}?page=2'
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug_3',
            description='Тестовое описание',
        )
        cls.GROUP_URL_PAGE_2 = f'{GROUP_URL_2}?page=2'
        Post.objects.bulk_create([
            Post(author=cls.user,
                 text='Тестовый пост' + str(i),
                 group=cls.group)for i in range(POST_NUMBER)
        ])
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_first_second_page_contains_right_records(self):
        """Первая и вторая страница содержат верное количество постов"""
        cache.clear()
        addresses = {
            POSTS_URL: settings.POST_NUMBER_ON_PAGE,
            GROUP_URL_2: settings.POST_NUMBER_ON_PAGE,
            PROFILE_URL_2: settings.POST_NUMBER_ON_PAGE,
            POSTS_URL_PAGE_2: 1,
            self.GROUP_URL_PAGE_2: 1,
            self.PROFILE_URL_PAGE_2: 1,
        }
        for address, post_number in addresses.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertEqual(
                    len(response.context['page_obj']), post_number)


class CommentFollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='some')
        cls.user_2 = User.objects.create_user(username='some_2')
        cls.user_3 = User.objects.create_user(username='some_3')
        cls.PROFILE_URL = reverse('posts:profile', args=[cls.user_3])
        cls.PROFILE_FOLLOW_URL = reverse(
            'posts:profile_follow', args=[cls.user_3])
        cls.PROFILE_UNFOLLOW_URL = reverse(
            'posts:profile_unfollow', args=[cls.user_3])
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug_4',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост3',
            group=cls.group,
        )
        cls.post_2 = Post.objects.create(
            author=cls.user_2,
            text='Тестовый пост4',
            group=cls.group,
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            text='Тестовый комментарий2',
            post=cls.post,
        )
        cls.POST_DETAIL_URL = reverse(
            'posts:post_detail', args=[cls.post.id])
        cls.POST_2_DETAIL_URL = reverse(
            'posts:post_detail', args=[cls.post_2.id])
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.another = Client()
        cls.another.force_login(cls.user_2)
        cls.another_2 = Client()
        cls.another_2.force_login(cls.user_3)

    def test_post_comment_in_comments_post(self):
        """Комментарий к определенному посту попал на страницу поста"""
        response = self.authorized_client.get(self.POST_DETAIL_URL)
        comments = response.context['post'].comments.all()
        self.assertEqual(comments.count(), 1)
        comment = comments[0]
        self.assertEqual(comment.post.id, self.comment.post.id)
        self.assertEqual(comment.id, self.comment.id)
        self.assertEqual(comment.text, self.comment.text)
        self.assertEqual(comment.author, self.comment.author)

    def test_user_follows_another_user(self):
        """Авторизованный пользователь может
        подписываться на другого пользователя.
        """
        self.another.get(self.PROFILE_FOLLOW_URL)
        self.assertTrue(Follow.objects.filter(
            user=self.user_2, author=self.user_3).exists())

    def test_user_unfollows_another_user(self):
        """Авторизованный пользователь может
        отписаться от других пользователей.
        """
        self.another.get(self.PROFILE_UNFOLLOW_URL)
        self.assertFalse(Follow.objects.filter(
            user=self.user_2, author=self.user_3).exists())
