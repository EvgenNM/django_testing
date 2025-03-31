from datetime import timedelta

import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.test.client import Client

from news.models import Comment, News


TODAY = timezone.now()
TEXT_COMMENT = 'Очень хайповый текстище'
NEW_TEXT_COMMENT = 'Новый текст коментария'


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Автор уже не тот ...')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст заметки',
    )
    return news


@pytest.fixture
def news_pk_reverse(news):
    return reverse('news:detail', args=(news.pk,))


@pytest.fixture
def reverse_news_home():
    return reverse('news:home')


@pytest.fixture
def news_list():
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=TODAY - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text=TEXT_COMMENT
    )
    return comment


@pytest.fixture
def comment_list(news, author):
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        comment = Comment.objects.create(
            news=news, author=author, text=f'{TEXT_COMMENT} {index}',
        )
        comment.created = TODAY + timedelta(days=index)
        comment.save()


@pytest.fixture
def reverse_comment_delete(comment):
    return reverse('news:delete', kwargs={'pk': comment.pk})


@pytest.fixture
def reverse_comment_edit(comment):
    return reverse('news:edit', kwargs={'pk': comment.pk})
