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
            'text': 'Текст измененный',
            'slug': 'Zagolovok'
        }
        cls.new_form_data_slug = {
            'title': 'Заголовок_очередной',
            'text': 'Текст измененный',
            'slug': 'Zagolovok-ok'
        }
        cls.url_edit = 'notes:edit'
        cls.url_delete = 'notes:delete'

    def create_author_form_date(self):
        """
        Фикстура создания авторизованным юзером 'Лев Толстой' новой заметки
        с использованием form_data
        """
        self.author_client.post(self.reverse_url, data=self.form_data)

    def create_author_new_form_data(self):
        """
        Фикстура создания авторизованным юзером 'Лев Толстой' новой заметки
        с использованием new_form_data
        """
        return self.author_client.post(
            self.reverse_url,
            data=self.new_form_data
        )
    
    def create_reader_form_data(self):
        """
        Фикстура создания авторизованным юзером 'Читатель простой' новой
        заметки с использованием form_data
        """
        self.reader_client.post(
            self.reverse_url,
            data=self.form_data
        )
        return Note.objects.get(pk=Note.objects.count())

    def test_create_notes_autorized(self):
        """Проверка, что залогиненный пользователь может создать заметку."""
        Note.objects.all().delete()
        self.create_author_form_date()
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()

        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.author, self.author)

    def test_create_notes_anonimus(self):
        """Проверка, что анонимный пользователь не может создать заметку."""
        count_notes_start = Note.objects.count()
        self.client.post(self.reverse_url, data=self.form_data)
        self.assertEqual(Note.objects.count(), count_notes_start)

    def test_unique_slug(self):
        """Проверка, что невозможно создать две заметки с одинаковым slug."""
        count_notes_start = Note.objects.count()
        self.create_author_form_date()
        self.assertEqual(Note.objects.count(), count_notes_start + 1)
        response = self.create_author_new_form_data()
        self.assertEqual(Note.objects.count(), count_notes_start + 1)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=self.new_form_data['slug'] + WARNING
        )

    def test_auto_slug(self):
        """
        Проверка, что если при создании заметки не заполнен slug,
        то он формируется автоматически, с помощью функции
        pytils.translit.slugify.
        """
        self.assertEqual(self.note.slug, slugify(self.note.title))

    def test_delete_update_our_notes(self):
        """
        Проверка, что пользователь может удалять свои заметки и
        не может удалять чужие.
        """
        not_note_reader = Note.objects.get(pk=Note.objects.count())
        self.create_reader_form_data()
        create_count = Note.objects.count()
        note_reader = Note.objects.get(pk=create_count)
        test_urls = [
            (self.url_delete, not_note_reader.slug, create_count),
            (self.url_delete, note_reader.slug, create_count - 1),
        ]
        for url, slug, result in test_urls:
            with self.subTest(url=url, slug=slug, result=result):
                self.reader_client.post(
                    reverse(url, kwargs={'slug': slug})
                )
                self.assertEqual(Note.objects.count(), result)

    def test_user_can_update_our_notes(self):
        """Проверка, что пользователь может редактировать свои заметки."""
        note_reader = self.create_reader_form_data()
        self.reader_client.post(
            reverse(self.url_edit, kwargs={'slug': note_reader.slug}),
            data=self.new_form_data_slug,
        )
        test_object = Note.objects.get(pk=note_reader.pk)
        test_list = [
            (test_object.text, self.new_form_data_slug['text']),
            (test_object.title, self.new_form_data_slug['title']),
            (test_object.author, self.reader),
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
        self.reader_client.post(
            reverse(self.url_edit, kwargs={'slug': self.note.slug}),
            data=self.new_form_data_slug,
        )
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
