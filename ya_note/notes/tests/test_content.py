from notes.forms import NoteForm
from notes.tests.base_test_class import BaseTestClass


class TestContent(BaseTestClass):
    """Тестирование сонтента."""

    def test_notes_object_list(self):
        """
        Проверка, что отдельная заметка передаётся на страницу
        со списком заметок в списке object_list в словаре context.
        """
        response = self.author_client.get(self.notes_list_reverse)
        self.assertIn(self.note, response.context['object_list'])

    def test_unique_notes(self):
        """
        Проверка, что в список заметок одного пользователя
        не попадают заметки другого пользователя.
        """
        response_author_object_list = self.author_client.get(
            self.notes_list_reverse
        ).context['object_list']
        response_reader_object_list = self.reader_client.get(
            self.notes_list_reverse
        ).context['object_list']

        for name, response_objects in (
            (self.author, response_author_object_list),
            (self.reader, response_reader_object_list)
        ):
            with self.subTest(name=name):
                self.assertEqual(
                    not response_objects
                    or all(
                        note.author == name for note in response_objects
                        ),
                    True
                )

    def test_create_edit_notes(self):
        """
        Проверка, что на страницы создания и редактирования
        заметки передаются формы.
        """
        for url in self.url_notes_add_eddit_response:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
