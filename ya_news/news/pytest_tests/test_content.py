from django.conf import settings

import pytest

from news.forms import CommentForm
from news.models import News


pytestmark = pytest.mark.django_db


def test_news_count(client, news_list, reverse_news_home):
    """
    Проверка, что количество новостей на главной странице
    соответствует NEWS_COUNT_ON_HOME_PAGE.
    """
    value = settings.NEWS_COUNT_ON_HOME_PAGE
    response = client.get(reverse_news_home)
    assert response.context['object_list'].count() == value
    assert News.objects.count() > value


def test_sorted_news(client, news_list, reverse_news_home):
    """
    Проверка, что новости отсортированы от самой свежей к
    самой старой. Свежие новости в начале списка.
    """
    response = client.get(reverse_news_home)
    home_list = response.context['object_list']
    date_list = [news.date for news in home_list]
    sorted_dates = sorted(date_list, reverse=True)
    assert date_list == sorted_dates


def test_sorted_comment(client, comment_list, news_pk_reverse):
    """
    Проверка, что комментарии на странице отдельной новости отсортированы в
    хронологическом порядке: старые в начале списка, новые — в конце.
    """
    response = client.get(news_pk_reverse)
    assert 'news' in response.context

    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    assert all_timestamps == sorted(all_timestamps)


@pytest.mark.parametrize(
    'name, result',
    (
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('client'), False),
    ),
)
def test_get_form_avtirized(name, result, news_pk_reverse):
    """
    Проверка, что анонимному пользователю недоступна форма для отправки
    комментария на странице отдельной новости, а авторизованному доступна.
    """
    response = name.get(news_pk_reverse)
    assert bool('form' in response.context) == result
    if result:
        assert isinstance(response.context['form'], CommentForm)
