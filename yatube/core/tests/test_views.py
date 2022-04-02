from django.test import Client, TestCase


class CoreViewsClass(TestCase):
    def setUp(self):
        self.guest = Client()

    def test_error_page(self):
        response = self.guest.get('/unexisting_page/')
        self.assertTemplateUsed(response, 'core/404.html')
        self.assertEqual(response.status_code, 404)
