from django.contrib.auth import get_user_model

from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestContent(TestCase):
    """Тестирование сонтента."""

    HOMEPAGE = 'notes:list'

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
        cls.reader_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client.force_login(cls.reader)

    def test_notes_object_list(self):
        """
        Проверка, что отдельная заметка передаётся на страницу
        со списком заметок в списке object_list в словаре context.
        """
        response = self.author_client.get(reverse(self.HOMEPAGE))
        self.assertIn('object_list', response.context)

    def test_unique_notes(self):
        """
        Проверка, что в список заметок одного пользователя
        не попадают заметки другого пользователя.
        """
        url = reverse(self.HOMEPAGE)
        response_author = self.author_client.get(url)
        response_reader = self.reader_client.get(url)
        self.assertEqual(response_author.context['object_list'].count(), 1)
        self.assertNotEqual(
            response_author.context['object_list'].count(),
            response_reader.context['object_list'].count()
        )

    def test_create_edit_notes(self):
        """
        Проверка, что на страницы создания и редактирования
        заметки передаются формы.
        """
        urls = [
            reverse('notes:add'),
            reverse('notes:edit', kwargs={'slug': self.note.slug})
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
