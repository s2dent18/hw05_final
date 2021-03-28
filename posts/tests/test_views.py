import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Comment, Follow, Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Группа для тестирования'
        )
        cls.post = Post.objects.create(
            text='Текст поста для тестирования',
            group=cls.group,
            author=User.objects.create_user(username='Authorized_user'),
            image=uploaded,
        )
        cls.empty_group = Group.objects.create(
            title='Пустая группа',
            slug='empty_group',
            description='Пустая группа для тестирования'
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.get(username=PostPagesTests.post.author)
        self.follower = User.objects.create(username='Test_follower')
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_follower = Client()
        self.authorized_follower.force_login(self.follower)

    def test_pages_use_correct_templates(self):
        """URL-адрес использует соответствующий шаблон"""
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
        сформированы с правильным контекстом"""
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
                post_image_0 = post_object.image
                self.assertEqual(post_author_0, PostPagesTests.post.author)
                self.assertEqual(post_pub_date_0, PostPagesTests.post.pub_date)
                self.assertEqual(post_text_0, PostPagesTests.post.text)
                self.assertEqual(post_group_0, PostPagesTests.post.group.id)
                self.assertEqual(post_image_0, PostPagesTests.post.image)

    def test_context_for_followers(self):
        """Контекст страницы follow сформирован корректно
        для подписанного пользователя"""
        Follow.objects.create(
            user=self.follower,
            author=self.user,
        )
        response = self.authorized_follower.get(reverse(
            'follow_index')
        )
        post_object = response.context['page'][0]
        post_author_0 = post_object.author
        post_pub_date_0 = post_object.pub_date
        post_text_0 = post_object.text
        post_group_0 = post_object.group.id
        post_image_0 = post_object.image
        self.assertEqual(post_author_0, PostPagesTests.post.author)
        self.assertEqual(post_pub_date_0, PostPagesTests.post.pub_date)
        self.assertEqual(post_text_0, PostPagesTests.post.text)
        self.assertEqual(post_group_0, PostPagesTests.post.group.id)
        self.assertEqual(post_image_0, PostPagesTests.post.image)

    def test_context_for_unfollowers(self):
        """Контекст страницы follow пуст
        для неподписанного пользователя"""
        Follow.objects.create(
            user=self.follower,
            author=self.user,
        )
        response = self.authorized_client.get(reverse(
            'follow_index')
        )
        post_object = response.context['page']
        post = PostPagesTests.post
        self.assertFalse(post.text in post_object)

    def test_user_post_show_correct_context(self):
        """Шаблон post сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse(
            'post', kwargs={
                'username': self.user.username,
                'post_id': self.post.id}))
        post_object = response.context['post']
        post_author_0 = post_object.author
        post_pub_date_0 = post_object.pub_date
        post_text_0 = post_object.text
        post_group_0 = post_object.group.id
        post_image_0 = post_object.image
        self.assertEqual(post_author_0, PostPagesTests.post.author)
        self.assertEqual(post_pub_date_0, PostPagesTests.post.pub_date)
        self.assertEqual(post_text_0, PostPagesTests.post.text)
        self.assertEqual(post_group_0, PostPagesTests.post.group.id)
        self.assertEqual(post_image_0, PostPagesTests.post.image)

    def test_new_page_show_correct_context(self):
        """Шаблон new сформирован с правильным контекстом"""
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

    def test_index_page_cache(self):
        """Кэш работает корректно"""
        response_before = self.authorized_client.get(reverse('index'))
        Post.objects.create(
            text='Новый пост',
            author=self.user,
        )
        response_after_add = self.authorized_client.get(reverse('index'))
        self.assertEqual(
            response_before.content,
            response_after_add.content
        )
        cache.clear()
        response_after_clear = self.authorized_client.get(reverse('index'))
        self.assertNotEqual(
            response_before.content,
            response_after_clear.content
        )

    def test_user_can_follow(self):
        """Активный пользователь может подписаться на посты автора"""
        follow_count = Follow.objects.count()
        response = self.authorized_follower.get(reverse(
            'profile_follow',
            kwargs={
                'username': self.user.username}))
        redirect_url = reverse(
            'profile',
            kwargs={'username': self.user.username})
        self.assertRedirects(response, redirect_url)
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        self.assertTrue(
            Follow.objects.filter(
                user=User.objects.get(username=self.follower.username),
                author=User.objects.get(username=self.user.username),
            ).exists()
        )

    def test_guest_can_not_follow(self):
        """Гость не может подписаться на посты автора"""
        follow_count = Follow.objects.count()
        kwargs = {'username': self.user.username}
        profile_follow = reverse('profile_follow', kwargs=kwargs)
        response = self.guest_client.get(profile_follow)
        login = reverse('login')
        redirect_url = f'{login}?next={profile_follow}'
        self.assertRedirects(response, redirect_url)
        self.assertEqual(Follow.objects.count(), follow_count)

    def test_user_can_unfollow(self):
        """Активный пользователь может отписаться от постов автора"""
        Follow.objects.create(
            user=self.follower,
            author=self.user,
        )
        follow_count = Follow.objects.count()
        response = self.authorized_follower.get(reverse(
            'profile_unfollow',
            kwargs={
                'username': self.user.username}))
        redirect_url = reverse(
            'profile',
            kwargs={'username': self.user.username})
        self.assertRedirects(response, redirect_url)
        self.assertEqual(Follow.objects.count(), follow_count - 1)
        self.assertFalse(
            Follow.objects.filter(
                user=User.objects.get(username=self.follower.username),
                author=User.objects.get(username=self.user.username),
            ).exists()
        )

    def test_user_can_create_comment(self):
        """Авторизованный пользователь может комментировать посты"""
        comments_count = Comment.objects.count()
        Comment.objects.create(
            text='Текст комментария',
            author=self.user,
            post=PostPagesTests.post
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                author=User.objects.get(username=self.user.username),
                post=PostPagesTests.post
            ).exists()
        )

    def test_guest_can_not_create_comment(self):
        """Неавторизованный пользователь не может комментировать посты"""
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый комментарий',
        }
        kwargs = {
            'username': self.user.username,
            'post_id': self.post.id}
        add_comment = reverse('add_comment', kwargs=kwargs)
        response = self.guest_client.post(
            add_comment,
            data=form_data,
            follow=True
        )
        login = reverse('login')
        redirect_url = f'{login}?next={add_comment}'
        self.assertRedirects(response, redirect_url)
        self.assertEqual(Comment.objects.count(), comments_count)


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
