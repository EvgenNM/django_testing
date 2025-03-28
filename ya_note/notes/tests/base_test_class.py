from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from http import HTTPStatus

from notes.models import Note


User = get_user_model()


class BaseTestClass(TestCase):
    """Проверка маршрутов приложения."""

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        slug = {'slug': cls.note.slug}
        cls.list_urls_note = [
            reverse('notes:detail', kwargs=slug),
            reverse('notes:edit', kwargs=slug),
            reverse('notes:delete', kwargs=slug),
        ]
        cls.list_urls_for_authorized = [
            reverse('notes:list'),
            reverse('notes:success'),
            reverse('notes:add'),
        ]
        cls.urls_home_login_logout_signup = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup',
        )
        cls.login_url = 'users:login'
