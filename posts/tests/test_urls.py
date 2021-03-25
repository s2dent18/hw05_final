from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Группа для тестирования'
        )
        cls.post = Post.objects.create(
            text='Текст поста для тестирования',
            group=cls.group,
            author=User.objects.create(username='test_user'),
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Authorized_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.author = PostURLTests.post.author
        self.authorized_author.force_login(self.author)

    def test_urls_exists_at_desired_location(self):
        """Страницы /, /group/<slug>/, /username, /username/post_id
        доступны любому пользователю"""
        templates = (
            '/',
            '/group/test_group/',
            '/test_user/',
            '/test_user/1/',
        )
        for template in templates:
            with self.subTest(template=template):
                response = self.guest_client.get(template)
                self.assertEqual(response.status_code, 200)

    def test_new_url_exists_at_desired_location(self):
        """Страница /new доступна авторизованному пользователю"""
        response = self.authorized_client.get('/new')
        self.assertEqual(response.status_code, 200)

    def test_user_post_edit_url_exists_at_desired_location(self):
        """Страница /username/post_id/edit доступна автору"""
        response = self.authorized_author.get(reverse(
            'post_edit',
            kwargs={
                'username': self.author.username,
                'post_id': self.post.id}))
        self.assertEqual(response.status_code, 200)

    def test_post_edit_guest_redirect(self):
        """Страница /username/post_id/edit недоступна
        анонимному пользователю"""
        response = self.guest_client.get(reverse(
            'post_edit',
            kwargs={
                'username': self.author.username,
                'post_id': self.post.id}))
        self.assertEqual(response.status_code, 302)

    def test_post_edit_not_author_redirect(self):
        """Страница /username/post_id/edit недоступна
        пользователю, не являющемуся автором"""
        response = self.authorized_client.get(reverse(
            'post_edit',
            kwargs={
                'username': self.author.username,
                'post_id': self.post.id}))
        self.assertEqual(response.status_code, 302)

    def test_post_edit_(self):
        """Страница /username/post_id/edit корректно редиректит
        пользователей без прав доступа"""
        response = self.authorized_client.get(reverse(
            'post_edit',
            kwargs={
                'username': self.author.username,
                'post_id': self.post.id}))
        redirect_url = '/test_user/1/'
        self.assertRedirects(response, redirect_url)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'index.html',
            '/group/test_group/': 'group.html',
            '/new': 'new.html',
            '/test_user/1/edit/': 'new.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_author.get(url)
                self.assertTemplateUsed(response, template)
