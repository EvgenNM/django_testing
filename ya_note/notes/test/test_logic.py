from django.contrib.auth import get_user_model

from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestLogic(TestCase):
    """Тестирование логики приложения."""

    ADD = reverse('notes:add')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.notes = Note.objects.create(
            title='Заголовок',
            text='Текст_отличен',
            author=cls.author,
        )

        cls.author_client = Client()
        cls.reader_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client.force_login(cls.reader)

        cls.form_data = {
            'title': 'Заголовок',
            'text': 'Текст',
            'slug': 'Zagolovok'
        }
        cls.new_form_data = {
            'title': 'Заголовок_очередной',
            'text': 'Текст измененный',
            'slug': 'Zagolovok'
        }
        cls.reverse_url = reverse('notes:add')

    def test_create_notes_autorized(self):
        """Проверка, что залогиненный пользователь может создать заметку."""
        self.author_client.post(self.reverse_url, data=self.form_data)
        self.assertEqual(Note.objects.count(), 2)
        note = Note.objects.get(pk=2)

        self.assertEqual(note.title, 'Заголовок')
        self.assertEqual(note.text, 'Текст')
        self.assertEqual(note.author, self.author)

    def test_create_notes_anonimus(self):
        """Проверка, что анонимный пользователь не может создать заметку."""
        self.client.post(self.reverse_url, data=self.form_data)
        self.assertEqual(Note.objects.count(), 1)

    def test_unique_slug(self):
        """Проверка, что невозможно создать две заметки с одинаковым slug."""
        self.author_client.post(self.reverse_url, data=self.form_data)
        self.assertEqual(Note.objects.count(), 2)
        self.author_client.post(self.reverse_url, data=self.new_form_data)
        self.assertEqual(Note.objects.get(pk=2).title, 'Заголовок')
        self.assertEqual(Note.objects.count(), 2)

    def test_auto_slug(self):
        """
        Проверка, что если при создании заметки не заполнен slug,
        то он формируется автоматически, с помощью функции
        pytils.translit.slugify.
        """
        self.assertEqual(self.notes.slug, 'zagolovok')

    def test_delete_update_our_notes(self):
        """
        Проверка, что пользователь может удалять свои заметки и
        не может удалять чужие.
        """
        self.reader_client.post(self.reverse_url, data=self.form_data)
        note_reader = Note.objects.get(pk=2)
        test_urls = [
            ('notes:delete', self.notes.slug, 2),
            ('notes:delete', note_reader.slug, 1),
        ]
        for url, slug, result in test_urls:
            with self.subTest(url=url, slug=slug, result=result):
                self.reader_client.post(
                    reverse(url, kwargs={'slug': slug})
                )
                self.assertEqual(Note.objects.count(), result)

    def test_cant_delete_update_other_notes(self):
        """
        Проверка, что пользователь может редактировать свои заметки и
        не может редактировать чужие.
        """
        self.reader_client.post(self.reverse_url, data=self.form_data)
        note_reader = Note.objects.get(pk=2)
        test_urls = [
            ('notes:edit', self.notes.slug, self.notes.text),
            ('notes:edit', note_reader.slug, self.new_form_data['text']),
        ]
        for url, slug, value in test_urls:
            with self.subTest(url=url, slug=slug, value=value):
                self.reader_client.post(
                    reverse(url, kwargs={'slug': slug}),
                    data=self.new_form_data,
                )
                self.assertEqual(Note.objects.get(slug=slug).text, value)
