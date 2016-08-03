from django.test import TestCase

from base.models import (
    ArtsNews, Audition, Production, ProductionCompany, Review
)
from base.tests.fixtures import ReviewFactory
from base.search_indexes import (
    ArtsNewsIndex, AuditionIndex, ProductionIndex, ProductionCompanyIndex,
    ReviewIndex
)


class ReviewIndexTestCase(TestCase):
    def setUp(self):
        self.review_index = ReviewIndex()

    def test_get_model(self):
        self.assertEqual(self.review_index.get_model(), Review)

    def test_index_queryset(self):
        published_review = ReviewFactory(is_published=True)
        unpublished_review = ReviewFactory(is_published=False)
        indexed = self.review_index.index_queryset()
        self.assertIn(published_review, indexed)
        self.assertNotIn(unpublished_review, indexed)


class AuditionIndexTestCase(TestCase):
    def test_get_model(self):
        self.assertEqual(AuditionIndex().get_model(), Audition)


class ProductionCompanyIndexTestCase(TestCase):
    def test_get_model(self):
        self.assertEqual(
            ProductionCompanyIndex().get_model(),
            ProductionCompany
        )


class ProductionIndexTestCase(TestCase):
    def test_get_model(self):
        self.assertEqual(ProductionIndex().get_model(), Production)


class ArtsNewsIndexTestCase(TestCase):
    def test_get_model(self):
        self.assertEqual(ArtsNewsIndex().get_model(), ArtsNews)
