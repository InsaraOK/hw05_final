from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

from core.models import CreatedModel

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        'название',
        max_length=200,
        help_text='название группы'
    )
    slug = models.SlugField(
        'метка перехода в адресной строке',
        unique=True,
        help_text='уникальная метка перехода в адресной строке'
    )
    description = models.TextField(
        'описание',
        help_text='краткое описание группы'
    )

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = 'группа'
        verbose_name_plural = 'группы'


class Post(CreatedModel):
    text = models.TextField(
        'текст',
        help_text='Напишите ваше сообщение'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='автор',
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='группа',
        help_text='Выберите группу',
    )
    image = models.ImageField(
        'картинка',
        upload_to=settings.POST_IMAGE_FOLDER_NAME,
        blank=True,
        null=True,
        help_text='Загрузите картинку'
    )

    def __str__(self) -> str:
        return self.text[0:15]

    class Meta(CreatedModel.Meta):
        verbose_name = 'пост'
        verbose_name_plural = 'посты'


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='пост',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='автор',
    )
    text = models.TextField(
        'текст',
        help_text='Напишите ваш комментарий'
    )

    def __str__(self) -> str:
        return self.text[0:15]

    class Meta(CreatedModel.Meta):
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='автор',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_combination',
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='no_self_follow',
            ),
        ]
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'
