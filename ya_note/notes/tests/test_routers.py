from http import HTTPStatus

from notes.tests.base_test_class import BaseTestClass


class TestRoutes(BaseTestClass):
    """Проверка маршрутов приложения."""

    def test_pages_availability(self):
        """
        Проверка доступности всем главной страницы,
        а также страницы регистрации пользователей,
        входа в учётную запись и выхода из неё.
        """
        for url in self.urls_home_login_logout_signup_reverse:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_anonimus_user(self):
        """
        Проверка перенаправления ананимного пользователя на страницу логина
        при попытке входа на страницу списка заметок,
        страницу успешного добавления записи,
        страницу добавления заметки, отдельной заметки,
        редактирования или удаления заметки.
        """
        for url in self.list_urls_note + self.list_urls_for_authorized:
            with self.subTest(url=url):
                redirect_url = f'{self.login_url_reverse}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_author_our_note(self):
        """
        Проверка доступности автору отдельной заметки,
        удаления и редактирования заметки, а также недоступности
        указанных страниц иному зарегистрированному пользователю.
        """
        users_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.reader_client, HTTPStatus.NOT_FOUND),
        )
        for name, status in users_statuses:
            for url in self.list_urls_note:
                with self.subTest(name=name, status=status, url=url):
                    response = name.get(url)
                    self.assertEqual(response.status_code, status)

    def test_acces_authorized_user(self):
        """
        Проверка доступа аутентифицированного пользователя к страницам
        со списком заметок, успешного добавления заметки,
        добавления новой заметки.
        """
        for url in self.list_urls_for_authorized:
            with self.subTest(url=url):
                response = self.reader_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
