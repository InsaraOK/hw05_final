import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import PostForm
from ..models import Group, Post, User, Comment


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

POST_CREATE_URL = reverse('posts:post_create')
USERNAME = 'auth'
USERNAME_2 = 'name'
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
class PostsFormsTests(TestCase):

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
        cls.POST_DETAIL_URL = reverse(
            'posts:post_detail', args=[cls.post.id])
        cls.POST_COMMENT_URL = reverse(
            'posts:add_comment', args=[cls.post.id])
        cls.guest = Client()
        cls.author = Client()
        cls.author.force_login(cls.user)
        cls.another = Client()
        cls.another.force_login(cls.user_2)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        cache.clear()
        form_data = {
            'text': 'Тестовый пост2',
            'group': self.group.id,
            'image': UPLOADED,
        }
        self.another.post(
            POST_CREATE_URL,
            data=form_data,
            follow=True,
        )
        post_list = Post.objects.exclude(id=self.post.id)
        self.assertEqual(post_list.count(), 1)
        post = post_list[0]
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.author, self.user_2)
        form_image_name = form_data['image'].name
        post_image_folder_name = Post._meta.get_field('image').upload_to
        self.assertEqual(post.image,
                         f'{post_image_folder_name}{form_image_name}'
                         )

    def test_edit_post(self):
        """Валидная форма изменяет запись в Post."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост3',
            'group': self.group_2.id,
            'image': UPLOADED_2,
        }
        response = self.author.post(
            self.POST_EDIT_URL,
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count)
        self.assertRedirects(response, self.POST_DETAIL_URL)
        post = response.context['post']
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.author, self.post.author)
        form_image_name = form_data['image'].name
        post_image_folder_name = Post._meta.get_field('image').upload_to
        self.assertEqual(post.image,
                         f'{post_image_folder_name}{form_image_name}'
                         )

    def test_create_comment(self):
        """Валидная форма создает комментарий в Post."""
        comments_list = self.post.comments.all()
        self.assertEqual(comments_list.count(), 0)
        form_data = {
            'text': 'Тестовый комментарий',
        }
        self.another.post(
            self.POST_COMMENT_URL,
            data=form_data,
            follow=True,
        )
        self.assertTrue(Comment.objects.filter(
            post=self.post,
            text=form_data['text']
        ).exists())
        self.assertEqual(comments_list.count(), 1)
        comment = comments_list[0]
        self.assertEqual(comment.text, form_data['text'])

    def test_form_labels(self):
        """labels в полях формы постов совпадает с ожидаемым"""
        labels = {
            'text': 'Текст поста',
            'group': 'Выберите группу',
        }
        for field, expected_value in labels.items():
            with self.subTest(field=field):
                label = self.form.fields[field].label
                self.assertEqual(label, expected_value)

    def test_form_help_texts(self):
        """help_texts в полях формы постов совпадает с ожидаемым"""
        help_texts = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_value in help_texts.items():
            with self.subTest(field=field):
                help_text = self.form.fields[field].help_text
                self.assertEqual(help_text, expected_value)

    def test_post_create_edit_detail_show_correct_context(self):
        """Шаблоны  post_create_edit_detail
        cформированы с правильным контекстом.
        """
        addresses = [
            POST_CREATE_URL,
            self.POST_EDIT_URL,
        ]
        for address in addresses:
            with self.subTest(address=address):
                response = self.author.get(address)
                self.assertIsInstance(response.context.get(
                    'form').fields.get('text'), forms.fields.CharField)
                self.assertIsInstance(response.context.get(
                    'form').fields.get('group'), forms.models.ModelChoiceField)
