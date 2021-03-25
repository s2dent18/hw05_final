from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField("group title", max_length=200)
    slug = models.SlugField(unique=True, max_length=50)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name="Текст", help_text="Напишите что-то")
    pub_date = models.DateTimeField(
        "date published",
        auto_now_add=True,
        db_index=True)
    group = models.ForeignKey(
        Group, on_delete=models.SET_NULL,
        blank=True, null=True, related_name="posts",
        help_text="Необязательное поле",
        verbose_name="Выберите группу"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="posts"
    )
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    class Meta:
        ordering = ("-pub_date",)

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE,
        related_name="comments"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="comments"
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Поле для вашего комментария',
    )
    created = models.DateTimeField("date published", auto_now_add=True)

    class Meta:
        ordering = ("-created",)

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="follower"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="following"
    )
