from http import HTTPStatus
from django.urls import reverse

import pytest
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('news')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    ),
)
def test_for_anonymous_user(client, name, args):
    """
    Проверка, что главная страница, страница отдельной новости доступна
    анонимному пользователю, а также страницы регистрации пользователей,
    входа в учётную запись и выхода из неё доступны всем пользователям.
    """
    url = reverse(name, args=(args.pk,) if args else args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:delete', pytest.lazy_fixture('comment')),
        ('news:edit', pytest.lazy_fixture('comment')),
    ),
)
@pytest.mark.parametrize(
    'faice, result',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
    ),
)
def test_update_delete_comment_author(name, args, faice, result):
    """
    Проверка, что страницы удаления и редактирования комментария доступны
    автору комментария, а также что авторизованный пользователь не может зайти
    на страницы редактирования или удаления чужих комментариев
    (возвращается ошибка 404).
    """
    response = faice.get(reverse(name, args=(args.pk,)))
    assert response.status_code == result


@pytest.mark.django_db
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
