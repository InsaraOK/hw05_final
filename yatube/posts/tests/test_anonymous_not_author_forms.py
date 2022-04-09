import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import PostForm
from ..models import Group, Post, User, Comment


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

POST_CREATE_URL = reverse('posts:post_create')
USERNAME = 'auth'
USERNAME_2 = 'name'
LOGIN_URL = reverse(settings.LOGIN_URL)
LOGIN_URL_POST_CREATE = f'{LOGIN_URL}?next={POST_CREATE_URL}'
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
UPLOADED_2 = SimpleUploadedFile(
    name='small_2.gif',
    content=SMALL_GIF,
    content_type='image/gif'
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class AnonymousPostsFormsTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.user_2 = User.objects.create_user(username=USERNAME_2)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug',
            description='Тестовое описание',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа2',
            slug='slug_2',
            description='Тестовое описание2',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )
        cls.form = PostForm()
        cls.POST_EDIT_URL = reverse('posts:post_edit', args=[cls.post.id])
        cls.POST_COMMENT_URL = reverse(
            'posts:add_comment', args=[cls.post.id])
        cls.guest = Client()
        cls.another = Client()
        cls.another.force_login(cls.user_2)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_anonymous_cannot_create_post(self):
        """Аноним не может создать запись в Post."""
        self.assertEqual(Post.objects.count(), 1)
        form_data = {
            'text': 'Тестовый пост4',
            'group': self.group.id,
            'image': UPLOADED,
        }
        responce = self.guest.post(
            POST_CREATE_URL,
            data=form_data,
            follow=True,
        )
        post_list = Post.objects.exclude(id=self.post.id)
        self.assertEqual(post_list.count(), 0)
        self.assertRedirects(responce, LOGIN_URL_POST_CREATE)

    def test_anonymous_and_not_author_cannot_edit_post(self):
        """Аноним и не автор не могут изменять запись в Post."""
        form_data = {
            'text': 'Тестовый пост3',
            'group': self.group_2.id,
            'image': UPLOADED_2,
        }
        clients = [self.guest, self.another]
        for client in clients:
            with self.subTest(client=client):
                client.post(
                    self.POST_EDIT_URL,
                    data=form_data,
                    follow=True
                )
                form_image_name = form_data['image'].name
                post_image_folder_name = Post._meta.get_field(
                    'image').upload_to
                self.assertFalse(Post.objects.filter(
                    id=self.post.id,
                    text=form_data['text'],
                    group=form_data['group'],
                    image=f'{post_image_folder_name}{form_image_name}'
                ).exists())

    def test_anonymous_cannot_create_comment(self):
        """Аноним не может создать комментарий в Post."""
        comments_list = self.post.comments.all()
        self.assertEqual(comments_list.count(), 0)
        form_data = {
            'text': 'Тестовый комментарий',
        }
        self.guest.post(
            self.POST_COMMENT_URL,
            data=form_data,
            follow=True,
        )
        self.assertFalse(Comment.objects.filter(
            post=self.post,
            text=form_data['text']
        ).exists())
        self.assertEqual(comments_list.count(), 0)
