from django.contrib.auth import get_user_model
from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
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

    def test_pages_availability(self):
        """
        Проверка доступности всем главной страницы,
        а также страницы регистрации пользователей,
        входа в учётную запись и выхода из неё.
        """
        urls = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup',
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
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
        login_url = reverse('users:login')
        for url in self.list_urls_note + self.list_urls_for_authorized:
            with self.subTest(url=url):
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_author_our_note(self):
        """
        Проверка доступности автору отдельной заметки,
        удаления и редактирования заметки, а также недоступности
        указанных страниц иному зарегистрированному пользователю.
        """
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for name, status in users_statuses:
            self.client.force_login(name)
            for url in self.list_urls_note:
                with self.subTest(name=name, status=status, url=url):
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_acces_authorized_user(self):
        """
        Проверка доступа аутентифицированного пользователя к страницам
        со списком заметок, успешного добавления заметки,
        добавления новой заметки.
        """
        for url in self.list_urls_for_authorized:
            self.client.force_login(self.reader)
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
