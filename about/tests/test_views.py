from django.test import Client, TestCase
from django.urls import reverse


class StaticViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_pages_accessible_by_names(self):
        """URLs, генерируемые при помощи имен about:author,
        about:tech, доступны."""
        reverse_names = (
            reverse('about:author'),
            reverse('about:tech'),
        )
        for reverse_name in reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(response.status_code, 200)

    def test_aboutr_pages_uses_correct_templates(self):
        """При запросе к about:
        применяются правильные шаблоны."""
        templates_page_names = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
        }
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
