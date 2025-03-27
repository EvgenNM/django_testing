from django.conf import settings
from django.urls import reverse
import pytest

from news.forms import CommentForm
from news.models import News



@pytest.mark.django_db
def test_news_count(client, news_list, news):
    """
    Проверка, что оличество новостей на главной странице — не более 10.
    """
    value = settings.NEWS_COUNT_ON_HOME_PAGE
    response = client.get(reverse('news:home'))
    home_list = response.context['object_list']
    assert home_list.count() == value
    assert News.objects.count() > value


@pytest.mark.django_db
def test_sorted_news(client, news_list):
    """
    Проверка, что новости отсортированы от самой свежей к
    самой старой. Свежие новости в начале списка.
    """
    response = client.get(reverse('news:home'))
    home_list = response.context['object_list']
    date_list = [news.date for news in home_list]
    sorted_dates = sorted(date_list, reverse=True)
    assert date_list == sorted_dates


@pytest.mark.django_db
def test_sorted_comment(client, news, comment_list):
    """
    Проверка, что комментарии на странице отдельной новости отсортированы в
    хронологическом порядке: старые в начале списка, новые — в конце.
    """
    response = client.get(reverse('news:detail', args=(news.pk,)))
    assert 'news' in response.context

    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    assert all_timestamps == sorted(all_timestamps)


@pytest.mark.django_db
@pytest.mark.parametrize(
        'name',
        (
            (pytest.lazy_fixture('author_client')),
            (pytest.lazy_fixture('client')),
        ),
)
def test_get_form_avtirized(name, news, client):
    """
    Проверка, что анонимному пользователю недоступна форма для отправки
    комментария на странице отдельной новости, а авторизованному доступна.
    """
    response = name.get(reverse('news:detail', args=(news.pk,)))
    if name == client:
        assert 'form' not in response.context
    else:
        assert 'form' in response.context
        assert isinstance(response.context['form'], CommentForm)
