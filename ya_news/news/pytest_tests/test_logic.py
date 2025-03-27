from django.urls import reverse

import pytest
from pytest_django.asserts import assertFormError

from .conftest import TEXT_COMMENT
from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
@pytest.mark.parametrize(
        'name, result',
        (
            (pytest.lazy_fixture('author_client'), 1),
            (pytest.lazy_fixture('client'), 0),
        ),
    )
def test_comment_create_author_client_and_cant_anonymous(name, result, news):
    """
    Проверка, что анонимный пользователь не может отправить комментарий,
    а также что авторизованный пользователь может отправить комментарий.
    """
    url = reverse('news:detail', args=(news.pk,))
    text_comment = {'text': 'Коментарий'}
    name.post(url, data=text_comment)
    response_result = Comment.objects.count()
    assert response_result == result
    if response_result:
        assert Comment.objects.get().text == text_comment['text']


@pytest.mark.parametrize(
        'name, result',
        (
            (pytest.lazy_fixture('author_client'), 0),
            (pytest.lazy_fixture('not_author_client'), 1),
        ),
    )
def test_author_can_delete_our_comment_and_cant_other(name, result, comment):
    """
    Проверка, что авторизованный пользователь может удалять свои
    комментарии и не может удалять чужие.
    """
    name.post(reverse('news:delete', args=(comment.pk,)))
    assert Comment.objects.count() == result


@pytest.mark.parametrize(
        'name, result',
        (
            (pytest.lazy_fixture('author_client'), 'Новый коментарий'),
            (pytest.lazy_fixture('not_author_client'), TEXT_COMMENT),
        ),
)
def test_author_can_edit_our_comment_and_cant_other(name, result, comment):
    """
    Проверка, что авторизованный пользователь может редактировать свои
    комментарии и не может редактировать чужие.
    """
    new_comment = {'text': 'Новый коментарий'}
    name.post(reverse('news:edit', args=(comment.pk,)), data=new_comment)
    assert Comment.objects.get().text == result


def test_user_cant_use_bad_words(author_client, news):
    """
    Проверка, что если комментарий содержит запрещённые слова,
    он не будет опубликован, а форма вернёт ошибку.
    """
    url = reverse('news:detail', args=(news.pk,))
    text_comment = {'text': f'Коментарий, {BAD_WORDS}!'}
    response = author_client.post(url, data=text_comment)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    assert Comment.objects.count() == 0
