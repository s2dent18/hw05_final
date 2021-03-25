from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
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
            author=User.objects.create_user(username='Authorized_user'),
        )
        cls.empty_group = Group.objects.create(
            title='Пустая группа',
            slug='empty_group',
            description='Пустая группа для тестирования'
        )

    def setUp(self):
        self.user = User.objects.get(username=PostPagesTests.post.author)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_use_correct_templates(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            'index.html': reverse('index'),
            'group.html': (reverse(
                'group_post',
                kwargs={'slug': PostPagesTests.group.slug})
            ),
            'new.html': reverse('new_post'),
        }
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_context_for_index_group_profile(self):
        """Шаблоны index, group, profile
        сформированы с правильным контекстом."""
        templates = (
            reverse('index'),
            reverse('group_post', kwargs={'slug': PostPagesTests.group.slug}),
            reverse('profile', kwargs={'username': self.user.username}),
        )
        for template in templates:
            with self.subTest(template=template):
                response = self.authorized_client.get(template)
                post_object = response.context['page'][0]
                post_author_0 = post_object.author
                post_pub_date_0 = post_object.pub_date
                post_text_0 = post_object.text
                post_group_0 = post_object.group.id
                self.assertEqual(post_author_0, PostPagesTests.post.author)
                self.assertEqual(post_pub_date_0, PostPagesTests.post.pub_date)
                self.assertEqual(post_text_0, PostPagesTests.post.text)
                self.assertEqual(post_group_0, PostPagesTests.post.group.id)

    def test_user_post_show_correct_context(self):
        """Шаблон post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'post', kwargs={
                'username': self.user.username,
                'post_id': self.post.id}))
        post_object = response.context['post']
        post_author_0 = post_object.author
        post_pub_date_0 = post_object.pub_date
        post_text_0 = post_object.text
        post_group_0 = post_object.group.id
        self.assertEqual(post_author_0, PostPagesTests.post.author)
        self.assertEqual(post_pub_date_0, PostPagesTests.post.pub_date)
        self.assertEqual(post_text_0, PostPagesTests.post.text)
        self.assertEqual(post_group_0, PostPagesTests.post.group.id)

    def test_new_page_show_correct_context(self):
        """Шаблон new сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Проверяем context словарь post_edit"""
        response = self.authorized_client.get(reverse(
            'post_edit',
            kwargs={
                'username': self.user.username,
                'post_id': self.post.id}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_add_correct(self):
        """Пост с указанной группой появляется только
        на главной странице, странице группы"""
        post = PostPagesTests.post
        templates = (
            reverse('index'),
            reverse('group_post', kwargs={'slug': PostPagesTests.group.slug})
        )
        for template in templates:
            with self.subTest(template=template):
                response = self.authorized_client.get(template)
                form_data = response.context['page'][0]
                self.assertEqual(post, form_data)
        response = self.authorized_client.get(reverse(
            'group_post', kwargs={'slug': PostPagesTests.empty_group.slug}))
        form_data = response.context['page']
        self.assertFalse(post.text in form_data)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Группа для тестирования'
        )
        cls.author = User.objects.create_user(username='Authorized_user')
        for i in range(12):
            Post.objects.create(
                text=(f'Текст поста для тестирования{i}'),
                group=cls.group,
                author=cls.author,
            )

    def setUp(self):
        self.user = User.objects.get(username=self.author.username)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_containse_ten_records(self):
        """В context index передается не более 10 постов"""
        response = self.authorized_client.get(reverse('index'))
        self.assertEqual(len(response.context.get('page').object_list), 10)
