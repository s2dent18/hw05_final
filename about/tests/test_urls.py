from django.test import Client, TestCase


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_urls_exists_at_desired_locations(self):
        """Проверка доступности адресов
        /about/author/ и /about/tech/."""
        urls = (
            '/about/author/',
            '/about/tech/',
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_about_urls_use_correct_templates(self):
        """Проверка шаблона адресов
        /about/author/ и /about/tech/."""
        templates = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        for url, template in templates.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
