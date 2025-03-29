from django.urls import reverse

import pytest
from pytest_django.asserts import assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from news.pytest_tests.conftest import NEW_TEXT_COMMENT, TEXT_COMMENT


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'name, result',
    (
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('client'), False),
    ),
)
def test_comment_create_author_client_and_cant_anonymous(
    name,
    result,
    news,
    news_pk_reverse,
    author
):
    """
    Проверка, что анонимный пользователь не может отправить комментарий,
    а также что авторизованный пользователь может отправить комментарий.
    """
    Comment.objects.all().delete()
    text_comment = {'text': 'Коментарий'}
    name.post(news_pk_reverse, data=text_comment)
    new_coment_count = Comment.objects.count()
    assert bool(new_coment_count) == result
    if result:
        new_object = Comment.objects.get()
        assert new_object.text == text_comment['text']
        assert new_object.author == author
        assert new_object.news == news



@pytest.mark.parametrize(
    'name, result',
    (
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('not_author_client'), False),
    ),
)
def test_author_can_delete_our_comment_and_cant_other(
    name, result, reverse_comment_delete
):
    """
    Проверка, что авторизованный пользователь может удалять свои
    комментарии и не может удалять чужие.
    """
    start_comment_count = Comment.objects.count()
    name.post(reverse_comment_delete)
    assert bool(start_comment_count - Comment.objects.count()) == result


@pytest.mark.parametrize(
    'name, result',
    (
        (pytest.lazy_fixture('author_client'), NEW_TEXT_COMMENT),
        (pytest.lazy_fixture('not_author_client'), TEXT_COMMENT),
    ),
)
def test_author_can_edit_our_comment_and_cant_other(name, result, comment):
    """
    Проверка, что авторизованный пользователь может редактировать свои
    комментарии и не может редактировать чужие.
    """
    new_comment = {'text': NEW_TEXT_COMMENT}
    name.post(reverse('news:edit', args=(comment.pk,)), data=new_comment)
    new_object = Comment.objects.get(pk=comment.pk)
    assert new_object.text == result
    assert new_object.author == comment.author
    assert new_object.news == comment.news


def test_user_cant_use_bad_words(author_client, news):
    """
    Проверка, что если комментарий содержит запрещённые слова,
    он не будет опубликован, а форма вернёт ошибку.
    """
    start_comment_count = Comment.objects.count()
    url = reverse('news:detail', args=(news.pk,))
    text_comment = {'text': f'Коментарий, {BAD_WORDS}!'}
    response = author_client.post(url, data=text_comment)
    assert start_comment_count == Comment.objects.count()
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
