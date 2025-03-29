from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

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
            text='Текст_отличен',
            author=cls.author,
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.list_urls_note = [
            reverse('notes:detail', args=(cls.note.slug,)),
            reverse('notes:edit', args=(cls.note.slug,)),
            reverse('notes:delete', args=(cls.note.slug,)),
        ]
        cls.list_urls_for_authorized = [
            reverse('notes:list'),
            reverse('notes:success'),
            reverse('notes:add'),
        ]
        cls.urls_home_login_logout_signup_reverse = (
            reverse('notes:home'),
            reverse('users:login'),
            reverse('users:logout'),
            reverse('users:signup'),
        )
        cls.url_notes_add_eddit_response = (
            reverse('notes:add'),
            reverse('notes:edit', kwargs={'slug': cls.note.slug})
        )
        cls.reverse_url = reverse('notes:add')
        cls.login_url_reverse = reverse('users:login')
        cls.notes_list_reverse = reverse('notes:list')
