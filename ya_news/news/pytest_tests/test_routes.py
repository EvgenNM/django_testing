from http import HTTPStatus

from django.urls import reverse

import pytest
from pytest_django.asserts import assertRedirects


pytestmark = pytest.mark.django_db


# Если не в том направлении двигаюсь,
# можно раскрыть шире и детальнее свои желания. Спасибо
@pytest.mark.parametrize(
    'name',
    (
        pytest.lazy_fixture('reverse_news_home'),
        pytest.lazy_fixture('news_pk_reverse'),
        reverse('users:login'),
        reverse('users:logout'),
        reverse('users:signup'),
    )
)
def test_for_anonymous_user(client, name):
    """
    Проверка, что главная страница, страница отдельной новости доступна
    анонимному пользователю, а также страницы регистрации пользователей,
    входа в учётную запись и выхода из неё доступны всем пользователям.
    """
    response = client.get(name)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'faice, url, result',
    (
        (
            pytest.lazy_fixture('not_author_client'),
            pytest.lazy_fixture('reverse_comment_edit'),
            HTTPStatus.NOT_FOUND
        ),
        (
            pytest.lazy_fixture('author_client'),
            pytest.lazy_fixture('reverse_comment_edit'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('not_author_client'),
            pytest.lazy_fixture('reverse_comment_delete'),
            HTTPStatus.NOT_FOUND
        ),
        (
            pytest.lazy_fixture('author_client'),
            pytest.lazy_fixture('reverse_comment_delete'),
            HTTPStatus.OK
        ),
    ),
)
def test_update_delete_comment_author(faice, url, result):
    """
    Проверка, что страницы удаления и редактирования комментария доступны
    автору комментария, а также что авторизованный пользователь не может зайти
    на страницы редактирования или удаления чужих комментариев
    (возвращается ошибка 404).
    """
    response = faice.get(url)
    assert response.status_code == result


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:delete', pytest.lazy_fixture('comment')),
        ('news:edit', pytest.lazy_fixture('comment')),
    ),
)
def test_redirect_anonimous(name, args, client):
    """
    Проверка, что при попытке перейти на страницу редактирования или
    удаления комментария анонимный пользователь перенаправляется
    на страницу авторизации.
    """
    url = reverse(name, args=(args.pk,))
    response = client.get(url)
    url_login = reverse('users:login')
    redirect_url = f'{url_login}?next={url}'
    assertRedirects(response, redirect_url)
