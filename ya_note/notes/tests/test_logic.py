from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from notes.tests.base_test_class import BaseTestClass


class TestLogic(BaseTestClass):
    """Тестирование логики приложения."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.form_data = {
            'title': 'Заголовок',
            'text': 'Текст',
            'slug': 'Zagolovok'
        }
        cls.new_form_data = {
            'title': 'Заголовок_очередной',
            'text': 'Текст измененный'
        }
        cls.new_form_data_slug = {
            'title': 'Заголовок_очередной',
            'text': 'Текст измененный',
            'slug': 'Zagolovok-ok'
        }

    def create_note(self, author, data):
        """Фикстура создания авторизованным юзером новой заметки."""
        return author.post(self.reverse_url, data=data)

    def create_note_duble_slug(self):
        """
        Фикстура создания авторизованным юзером новой заметки
        с уже имеющимся slug.
        """
        note = Note.objects.all().last()
        data = self.form_data
        data['slug'] = note.slug
        return self.create_note(self.author_client, data)

    def get_urls_delete_notes(self, *args):
        """Фикстура получения адресов удаления заметок по переданным slug."""
        urls = [
            reverse(self.url_delete, kwargs={'slug': slug})
            for slug in args
        ]
        return urls


    def test_create_notes_autorized(self):
        """Проверка, что залогиненный пользователь может создать заметку."""
        Note.objects.all().delete()
        self.create_note(self.author_client, self.form_data)
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()

        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.author, self.author)

    def test_create_notes_anonimus(self):
        """Проверка, что анонимный пользователь не может создать заметку."""
        count_notes_start = Note.objects.count()
        self.create_note(self.client, self.form_data)
        self.assertEqual(Note.objects.count(), count_notes_start)

    def test_unique_slug(self):
        """Проверка, что невозможно создать две заметки с одинаковым slug."""
        count_notes_start = Note.objects.count()
        response = self.create_note_duble_slug()
        self.assertEqual(Note.objects.count(), count_notes_start)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=self.form_data['slug'] + WARNING
        )

    def test_auto_slug(self):
        """
        Проверка, что если при создании заметки не заполнен slug,
        то он формируется автоматически, с помощью функции
        pytils.translit.slugify.
        """
        self.create_note(self.author_client, self.new_form_data)
        note = Note.objects.all().last()
        self.assertEqual(note.slug, slugify(note.title))

    def test_delete_update_our_notes(self):
        """
        Проверка, что пользователь может удалять свои заметки и
        не может удалять чужие.
        """
        self.create_note(self.reader_client, self.form_data)
        note_reader = Note.objects.all().last()
        create_count = Note.objects.count()
        test_count = [create_count, create_count - 1]
        urls = self.get_urls_delete_notes(self.note.slug, note_reader.slug)
        for url, count in zip(urls, test_count):
            with self.subTest(url=url, count=count):
                self.reader_client.post(url)
                self.assertEqual(Note.objects.count(), count)

    def test_user_can_update_our_notes(self):
        """Проверка, что пользователь может редактировать свои заметки."""
        self.author_client.post(
            self.notes_edit,
            data=self.new_form_data_slug,
        )
        test_object = Note.objects.get(pk=self.note.pk)
        test_list = [
            (test_object.text, self.new_form_data_slug['text']),
            (test_object.title, self.new_form_data_slug['title']),
            (test_object.author, self.author),
            (test_object.slug, self.new_form_data_slug['slug']),
        ]
        for note_value, form_value in test_list:
            with self.subTest(note_value=note_value, form_value=form_value):
                self.assertEqual(note_value, form_value)

    def test_user_cant_update_other_notes(self):
        """Проверка, что пользователь не может редактировать чужие заметки."""
        old_value_note = (
            self.note.text,
            self.note.title,
            self.note.author,
            self.note.slug
        )
        self.reader_client.post(self.notes_edit, data=self.new_form_data_slug)
        test_object = Note.objects.get(pk=self.note.pk)
        test_value_note = (
            test_object.text,
            test_object.title,
            test_object.author,
            test_object.slug,
        )
        for old_value, test_value in zip(old_value_note, test_value_note):
            with self.subTest(old_value=old_value, test_value=test_value):
                self.assertEqual(old_value, test_value)
