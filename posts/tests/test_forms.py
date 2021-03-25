from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post, User


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = PostForm()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Группа для тестирования'
        )
        cls.post = Post.objects.create(
            group=cls.group,
            text='Тестовый текст',
            author=User.objects.create_user(username='Authorized_user')
        )

    def setUp(self):
        self.user = User.objects.get(
            username=PostCreateFormTests.post.author.username)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_edit_post(self):
        """Валидная форма редактирует запись в Post."""
        posts_count = Post.objects.count()

        form_data = {
            'text': 'Тестовый текст из формы',
            'group': PostCreateFormTests.group.id,
        }
        response = self.authorized_client.post(reverse(
            'post_edit',
            kwargs={'username': self.user.username, 'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'post', kwargs={
                'username': self.user.username,
                'post_id': self.post.id}))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=PostCreateFormTests.group.id
            ).exists()
        )

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()

        form_data = {
            'text': 'Тестовый текст из формы',
            'group': PostCreateFormTests.group.id,
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=PostCreateFormTests.group
            ).exists()
        )
