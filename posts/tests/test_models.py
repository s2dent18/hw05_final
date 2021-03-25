from django.test import TestCase

from posts.models import Group, Post, User


class PostModelTest(TestCase):
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
            author=User.objects.create_user(username='Test_user'),
        )

    def test_verbose_name(self):
        """verbose_name в полях group, text совпадают с ожидаемыми"""
        post = PostModelTest.post
        field_verboses = {
            'group': 'Выберите группу',
            'text': 'Текст'
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        """help_text полей text и group совпадает с ожидаемым."""
        post = PostModelTest.post
        help_texts = {
            'group': 'Необязательное поле',
            'text': 'Напишите что-то'
        }
        for field, text in help_texts.items():
            with self.subTest(field=field):
                help_text = post._meta.get_field(field).help_text
                self.assertEqual(help_text, text)

    def test_group_str_method(self):
        """Метод __str__ для group работает корректно"""
        group = PostModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    def test_post_str_method(self):
        """Метод __str__ для post работает корректно"""
        post = PostModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))
