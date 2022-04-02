from django.test import TestCase

from ..models import Group, Post, User, Comment, Follow


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            text='Тестовый комментарий',
            post=cls.post,
        )

    def test_post_model_have_correct_object_names(self):
        """Проверяем, что у моделли Поста корректно работает __str__."""
        self.assertEqual(self.post.text[0:15], str(self.post))

    def test_group_model_have_correct_object_name(self):
        """Проверяем, что у моделли Группы корректно работает __str__."""
        self.assertEqual(self.group.title, str(self.group))

    def test_comment_model_have_correct_object_name(self):
        """Проверяем, что у моделли Комментария корректно работает __str__."""
        self.assertEqual(self.comment.text[0:15], str(self.comment))

    def test_post_verbose_name(self):
        """verbose_name в полях модели постов совпадает с ожидаемым."""
        field_verboses = {
            'text': 'текст',
            'pub_date': 'дата публикации',
            'author': 'автор',
            'group': 'группа',
            'image': 'картинка'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Post._meta.get_field(field).verbose_name, expected_value)

    def test_group_verbose_name(self):
        """verbose_name в полях модели группы совпадает с ожидаемым."""
        field_verboses = {
            'title': 'название',
            'slug': 'метка перехода в адресной строке',
            'description': 'описание',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Group._meta.get_field(field).verbose_name, expected_value)

    def test_post_help_text(self):
        """help_text в полях модели поста совпадает с ожидаемым."""
        field_help_texts = {
            'text': 'Напишите ваше сообщение',
            'group': 'Выберите группу',
            'image': 'Загрузите картинку'
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Post._meta.get_field(field).help_text, expected_value)

    def test_group_help_text(self):
        """help_text в полях модели группы совпадает с ожидаемым."""
        field_help_texts = {
            'title': 'название группы',
            'slug': 'уникальная метка перехода в адресной строке',
            'description': 'краткое описание группы',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Group._meta.get_field(field).help_text, expected_value)

    def test_comment_verbose_name(self):
        """verbose_name в полях модели комментариев совпадает с ожидаемым."""
        field_verboses = {
            'post': 'пост',
            'author': 'автор',
            'text': 'текст',
            'pub_date': 'дата публикации',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Comment._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_comment_help_text(self):
        """help_text в полях модели комментария совпадает с ожидаемым."""
        self.assertEqual(
            Comment._meta.get_field('text').help_text,
            'Напишите ваш комментарий'
        )

    def test_follow_verbose_name(self):
        """verbose_name в полях модели подписки совпадает с ожидаемым."""
        field_verboses = {
            'user': 'подписчик',
            'author': 'автор',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Follow._meta.get_field(field).verbose_name,
                    expected_value
                )
