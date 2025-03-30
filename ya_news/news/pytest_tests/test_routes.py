from http import HTTPStatus

from django.urls import reverse
import pytest
from pytest_django.asserts import assertRedirects


pytestmark = pytest.mark.django_db


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
        (
            pytest.lazy_fixture('client'),
            pytest.lazy_fixture('reverse_news_home'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('client'),
            pytest.lazy_fixture('news_pk_reverse'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('client'),
            reverse('users:login'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('client'),
            reverse('users:logout'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('client'),
            reverse('users:signup'),
            HTTPStatus.OK
        )
    ),
)
def test_urls_author_not_author_anonimous(faice, url, result):
    """
    Проверка, что страницы удаления и редактирования комментария доступны
    автору комментария, а также что авторизованный пользователь не может зайти
    на страницы редактирования или удаления чужих комментариев
    (возвращается ошибка 404).
    """
    response = faice.get(url)
    assert response.status_code == result


@pytest.mark.parametrize(
    'name',
    (
        pytest.lazy_fixture('reverse_comment_delete'),
        pytest.lazy_fixture('reverse_comment_edit'),
    )
)
def test_redirect_anonimous(name, client):
    """
    Проверка, что при попытке перейти на страницу редактирования или
    удаления комментария анонимный пользователь перенаправляется
    на страницу авторизации.
    """
    response = client.get(name)
    url_login = reverse('users:login')
    redirect_url = f'{url_login}?next={name}'
    assertRedirects(response, redirect_url)
