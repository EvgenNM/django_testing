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
        # Получаем объекты response при get-запросе на страницу списка заметок
        # авторизованных юзеров.
        # в BaseTestClass  создана одна заметка, где автор self.author:
        # в списке первого (author_client) объекта должна быть одна заметка,
        # т.к. он ее автор
        response_author = self.author_client.get(self.notes_list_reverse)
        # в списке второго (reader_client) объекта не должно быть заметок
        response_reader = self.reader_client.get(self.notes_list_reverse)
        self.assertEqual(
            response_author.context['object_list'].get(pk=1).author,
            self.author
        )
        # Или?
        # for note in response_author.context['object_list']:
        #     with self.subTest(note=note, author=self.author):
        #         self.assertEqual(note.author, self.author)
        self.assertEqual(response_reader.context['object_list'].count(), 0)

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
