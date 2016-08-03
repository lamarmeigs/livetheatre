from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from base.feeds import AggregatedFeed
from base.tests.fixtures import (
    ArtsNewsFactory, AuditionFactory, ProductionFactory,
    ProductionCompanyFactory, ReviewFactory, ReviewerFactory,
)


class AggregatedFeedTestCase(TestCase):
    def setUp(self):
        self.feed = AggregatedFeed()

    def test_class_attributes(self):
        self.assertEqual(AggregatedFeed.title, 'CTX Live Theatre')
        self.assertEqual(AggregatedFeed.link, '/')

    def test_items(self):
        now = timezone.now()
        one_day_ago = now - timedelta(days=1)

        news = ArtsNewsFactory()
        audition = AuditionFactory()
        production = ProductionFactory()
        review = ReviewFactory(
            is_published=True,
            published_on=one_day_ago,
            production=production,
        )

        self.assertEqual(
            self.feed.items(),
            [production, audition, news, review]
        )

    def test_item_title(self):
        news = ArtsNewsFactory()
        self.assertEqual(self.feed.item_title(news), news.title)

    def test_item_description(self):
        news = ArtsNewsFactory(content='This is the news content.')
        self.assertEqual(self.feed.item_description(news), news.content)
        prod = ProductionFactory(description='This is a production.')
        self.assertEqual(self.feed.item_description(prod), prod.description)

    def test_item_pubdate(self):
        news = ArtsNewsFactory(created_on=timezone.now() - timedelta(days=1))
        self.assertEqual(self.feed.item_pubdate(news), news.created_on)
        review = ReviewFactory(published_on=timezone.now() - timedelta(days=2))
        self.assertEqual(self.feed.item_pubdate(review), review.published_on)
        company = ProductionCompanyFactory()
        self.assertIsNotNone(self.feed.item_pubdate(company))

    def test_item_categories(self):
        prod = ProductionFactory()
        self.assertEqual(self.feed.item_categories(prod), ['Productions'])
        review = ReviewFactory()
        self.assertEqual(self.feed.item_categories(review), ['Reviews'])
        audition = AuditionFactory()
        self.assertEqual(self.feed.item_categories(audition), ['Auditions'])
        news = ArtsNewsFactory()
        self.assertEqual(self.feed.item_categories(news), ['News'])
        reviewer = ReviewerFactory()
        self.assertEqual(self.feed.item_categories(reviewer), [])
