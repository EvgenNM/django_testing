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
        cls.note_reader = Note.objects.create(
            title='Заголовок читателя',
            text='Текст_середнячковый',
            author=cls.reader,
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.reverse_url = reverse('notes:add')
        cls.login_url_reverse = reverse('users:login')
        cls.notes_list_reverse = reverse('notes:list')
        cls.notes_edit = reverse('notes:edit', kwargs={'slug': cls.note.slug})
        cls.delete_note_author = reverse(
            'notes:delete', kwargs={'slug': cls.note.slug}
        )
        cls.delete_note_reader = reverse(
            'notes:delete', kwargs={'slug': cls.note_reader.slug}
        )

        cls.list_urls_note = [
            reverse('notes:detail', args=(cls.note.slug,)),
            cls.notes_edit,
            cls.delete_note_author,
        ]
        cls.list_urls_for_authorized = [
            reverse('notes:list'),
            reverse('notes:success'),
            cls.reverse_url,
        ]
        cls.urls_home_login_logout_signup_reverse = (
            reverse('notes:home'),
            cls.login_url_reverse,
            reverse('users:logout'),
            reverse('users:signup'),
        )
        cls.url_notes_add_eddit_response = (
            cls.reverse_url,
            cls.notes_edit,
        )
