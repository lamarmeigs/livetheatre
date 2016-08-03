from django.contrib import admin
from django.db import models
from django.http import HttpRequest
from django.test import TestCase
from mock import patch
from tinymce.widgets import TinyMCE

from base.admin import (
    ArtsNewsAdmin, AuditionAdmin, ExternalReviewAdmin,
    NewsSlideshowImageInline, ProductionCompanyAdmin, PlayAdmin,
    ProductionAdmin, ProductionPosterInline, ReviewAdmin, ReviewerAdmin,
    VenueAdmin
)
from base.models import Review
from base.tests.fixtures import ReviewFactory


class ReviewAdminTestCase(TestCase):
    def setUp(self):
        self.review_admin = ReviewAdmin(Review, admin.site)

    def test_class_attributes(self):
        self.assertTrue(ReviewAdmin.actions_on_bottom)
        self.assertTrue(ReviewAdmin.save_on_top)
        self.assertEqual(ReviewAdmin.exclude, ('slug',))
        self.assertEqual(
            ReviewAdmin.list_display,
            ('get_title', 'is_published', 'published_on')
        )
        self.assertEqual(ReviewAdmin.ordering, ('published_on',))
        self.assertEqual(
            ReviewAdmin.search_fields,
            [
                'title', 'production__play__title',
                'production__production_company__name'
            ]
        )
        self.assertEqual(
            ReviewAdmin.related_search_fields,
            {'production': ('play__title', 'production_company__name')}
        )
        self.assertEqual(
            ReviewAdmin.actions,
            ['publish_reviews', 'unpublish_reviews']
        )
        self.assertIsInstance(
            ReviewAdmin.formfield_overrides[models.TextField]['widget'],
            TinyMCE
        )

    def test_publish_reviews(self):
        review = ReviewFactory(is_published=False)
        request = HttpRequest()
        with patch.object(self.review_admin, 'message_user') as mock_message:
            self.review_admin.publish_reviews(request, Review.objects.all())
        review = Review.objects.get(pk=review.pk)
        self.assertTrue(review.is_published)
        mock_message.assert_called_once_with(request, '1 review published.')

    def test_unpublish_reviews(self):
        review = ReviewFactory(is_published=True)
        request = HttpRequest()
        with patch.object(self.review_admin, 'message_user') as mock_message:
            self.review_admin.unpublish_reviews(request, Review.objects.all())
        review = Review.objects.get(pk=review.pk)
        self.assertFalse(review.is_published)
        mock_message.assert_called_once_with(request, '1 review unpublished.')


class AuditionAdminTestCase(TestCase):
    def test_class_attributes(self):
        self.assertTrue(AuditionAdmin.actions_on_bottom)
        self.assertTrue(AuditionAdmin.save_on_top)
        self.assertEqual(AuditionAdmin.exclude, ('slug',))
        self.assertEqual(
            AuditionAdmin.list_display,
            ('title', 'start_date', 'end_date')
        )
        self.assertEqual(AuditionAdmin.ordering, ('start_date',))
        self.assertEqual(
            AuditionAdmin.search_fields,
            ['title', 'production_company__name', 'play__title']
        )
        self.assertEqual(
            AuditionAdmin.related_search_fields,
            {
                'play': ('title',),
                'production_company': ('name',)
            }
        )
        self.assertIsInstance(
            AuditionAdmin.formfield_overrides[models.TextField]['widget'],
            TinyMCE
        )


class ProductionCompanyAdminTestCase(TestCase):
    def test_class_attributes(self):
        self.assertEqual(
            ProductionCompanyAdmin.prepopulated_fields,
            {'slug': ('name',)}
        )
        self.assertTrue(ProductionCompanyAdmin.actions_on_bottom)
        self.assertTrue(ProductionCompanyAdmin.save_on_top)
        self.assertEqual(ProductionCompanyAdmin.list_display, ('name',))
        self.assertEqual(
            ProductionCompanyAdmin.search_fields,
            ['name', 'company_site']
        )
        self.assertIsInstance(
            ProductionCompanyAdmin.formfield_overrides[models.TextField]['widget'],
            TinyMCE
        )


class ProductionAdminTestCase(TestCase):
    def test_class_attributes(self):
        self.assertEqual(ProductionAdmin.exclude, ('slug',))
        self.assertTrue(ProductionAdmin.actions_on_bottom)
        self.assertTrue(ProductionAdmin.save_on_top)
        self.assertEqual(
            ProductionAdmin.list_display,
            ('play', 'production_company', 'start_date', 'end_date')
        )
        self.assertEqual(
            ProductionAdmin.list_filter,
            ('play__title', 'production_company__name', 'venue__name')
        )
        self.assertEqual(ProductionAdmin.ordering, ('start_date',))
        self.assertEqual(
            ProductionAdmin.search_fields,
            ['play__title', 'production_company__name', 'venue__name']
        )
        self.assertEqual(
            ProductionAdmin.related_search_fields,
            {
                'play': ('title',),
                'production_company': ('name',),
                'venue': ('name', 'address__line_1'),
            }
        )
        self.assertIsInstance(
            ProductionAdmin.formfield_overrides[models.TextField]['widget'],
            TinyMCE
        )
        self.assertEqual(ProductionAdmin.inlines, [ProductionPosterInline])


class PlayAdminTestCase(TestCase):
    def test_class_attributes(self):
        self.assertTrue(PlayAdmin.actions_on_bottom)
        self.assertTrue(PlayAdmin.save_on_top)
        self.assertEqual(PlayAdmin.list_display, ('title', 'playwright'))
        self.assertEqual(PlayAdmin.search_fields, ['title', 'playwright'])
        self.assertIsInstance(
            PlayAdmin.formfield_overrides[models.TextField]['widget'],
            TinyMCE
        )


class VenueAdminTestCase(TestCase):
    def test_class_attributes(self):
        self.assertEqual(VenueAdmin.prepopulated_fields, {'slug': ('name',)})
        self.assertTrue(VenueAdmin.actions_on_bottom)
        self.assertTrue(VenueAdmin.save_on_top)
        self.assertEqual(VenueAdmin.list_display, ('name', 'address'))
        self.assertEqual(VenueAdmin.list_filter, ('address__city',))
        self.assertEqual(
            VenueAdmin.search_fields,
            ['name', 'address__line_1', 'address__city']
        )
        self.assertEqual(
            VenueAdmin.related_search_fields,
            {'address': ('line_1', 'line_2', 'city', 'zip_code')}
        )
        self.assertIsInstance(
            VenueAdmin.formfield_overrides[models.TextField]['widget'],
            TinyMCE
        )


class ArtsNewsAdminTestCase(TestCase):
    def test_class_attributes(self):
        self.assertEqual(
            ArtsNewsAdmin.prepopulated_fields,
            {'slug': ('title',)}
        )
        self.assertTrue(ArtsNewsAdmin.actions_on_bottom)
        self.assertTrue(ArtsNewsAdmin.save_on_top)
        self.assertEqual(ArtsNewsAdmin.list_display, ('title', 'created_on'))
        self.assertEqual(ArtsNewsAdmin.ordering, ('created_on',))
        self.assertEqual(
            ArtsNewsAdmin.search_fields,
            ['title', 'external_url']
        )
        self.assertEqual(
            ArtsNewsAdmin.related_search_fields,
            {
                'related_production': (
                    'play__title',
                    'production_company__name'
                ),
                'related_company': ('name',)
            }
        )
        self.assertIsInstance(
            ArtsNewsAdmin.formfield_overrides[models.TextField]['widget'],
            TinyMCE
        )
        self.assertEqual(ArtsNewsAdmin.inlines, [NewsSlideshowImageInline])


class ReviewerAdminTestCase(TestCase):
    def test_class_attributes(self):
        self.assertTrue(ReviewerAdmin.actions_on_bottom)
        self.assertTrue(ReviewerAdmin.save_on_top)
        self.assertTrue(
            ReviewerAdmin.list_display,
            ('full_name', 'review_count')
        )
        self.assertIsInstance(
            ReviewerAdmin.formfield_overrides[models.TextField]['widget'],
            TinyMCE
        )


class ExternalReviewAdminTestCase(TestCase):
    def test_class_attributes(self):
        self.assertTrue(ExternalReviewAdmin.actions_on_bottom)
        self.assertTrue(ExternalReviewAdmin.save_on_top)
        self.assertEqual(
            ExternalReviewAdmin.list_display,
            ('production', 'source_name', 'review_url')
        )
        self.assertEqual(
            ExternalReviewAdmin.search_fields,
            [
                'production__play__title', 'source_name', 'review_url',
                'production__production_company__name'
            ]
        )
        self.assertEqual(
            ExternalReviewAdmin.related_search_fields,
            {'production': ('play__title', 'production_company__name')}
        )
