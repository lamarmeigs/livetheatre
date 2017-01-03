from datetime import datetime, timedelta

from django.test import TestCase
from django.utils import timezone
from django.utils.text import slugify
from mock import patch

from base.models import (
    Audition, AuditionManager, DaysBase, Production, Reviewer, Venue, ArtsNews,
    ProductionCompany, SlideshowImage
)
from base.tests.fixtures import (
    AddressFactory, ArtsNewsFactory, AuditionFactory, ExternalReviewFactory,
    NewsSlideshowImageFactory, PlayFactory, ProductionFactory,
    ProductionCompanyFactory, ReviewFactory, ReviewerFactory, VenueFactory
)


class ReviewTestCase(TestCase):
    def test_get_title(self):
        review = ReviewFactory(title='Some Title')
        self.assertEqual(review.get_title(), review.title)

        review = ReviewFactory()
        self.assertEqual(
            review.get_title(),
            'Review: {}'.format(review.production)
        )

    def test_get_slug(self):
        review = ReviewFactory()
        self.assertEqual(review.get_slug(), slugify(review.get_title()[:47]))
        review_2 = ReviewFactory()
        self.assertEqual(
            review_2.get_slug(),
            '{}1'.format(slugify(review.get_title()[:47]))
        )

    def test_publish(self):
        review = ReviewFactory(is_published=False, published_on=None)
        with patch.object(review, 'save') as mock_save:
            review.publish()
        mock_save.assert_called_once_with()
        self.assertTrue(review.is_published)
        self.assertIsNotNone(review.published_on)

    def test_unpublish(self):
        review = ReviewFactory(is_published=True, published_on=timezone.now())
        with patch.object(review, 'save') as mock_save:
            review.unpublish()
        mock_save.assert_called_once_with()
        self.assertFalse(review.is_published)

    def test_save(self):
        review = ReviewFactory(pk=None, title=None, slug=None)
        with patch('django.db.models.Model.save') as mock_save:
            review.save()
        self.assertEqual(review.title, review.get_title())
        self.assertEqual(review.slug, review.get_slug())
        mock_save.assert_called_once_with()

    def test_save_published_review(self):
        review = ReviewFactory(is_published=True, published_on=None)
        with patch('django.db.models.Model.save') as mock_save:
            review.save()
        self.assertIsNotNone(review.published_on)
        mock_save.assert_called_once_with()

    def test_get_absolute_url(self):
        review = ReviewFactory()
        try:
            absolute_url = review.get_absolute_url()
        except Exception as e:
            self.fail(
                'Review.get_absolute_url() unexpectedly raised error: '
                '{}'.format(str(e))
            )
        self.assertIsInstance(absolute_url, unicode)

    def test_unicode(self):
        review = ReviewFactory()
        self.assertEqual(review.__unicode__(), unicode(review.get_title()))


class DaysBaseTestCase(TestCase):
    def test_get_last_sequential_day_index(self):
        days_base = DaysBase(
            on_monday=True,
            on_tuesday=True,
            on_wednesday=True
        )
        self.assertEqual(days_base.get_last_sequential_day_index(), 2)

        days_base = DaysBase(on_saturday=True, on_sunday=True, on_monday=True)
        self.assertEqual(
            days_base.get_last_sequential_day_index(start_on=5, wrap=False),
            6
        )
        self.assertEqual(
            days_base.get_last_sequential_day_index(start_on=5),
            0
        )

    def test_week_booleans(self):
        days_base = DaysBase(
            on_monday=True,
            on_wednesday=True,
            on_thursday=True,
            on_saturday=True
        )
        self.assertEqual(
            days_base._week_booleans(),
            [True, False, True, True, False, True, False]
        )

    def test_has_weekly_schedule(self):
        days_base = DaysBase()
        self.assertFalse(days_base.has_weekly_schedule())
        days_base = DaysBase(on_friday=True)
        self.assertTrue(days_base.has_weekly_schedule())

    def test_get_verbose_week_description(self):
        days_base = DaysBase()
        with patch.object(days_base, 'get_week_description') as mock:
            days_base.get_verbose_week_description()
        mock.assert_called_once_with(verbose=True)

    def test_get_week_description(self):
        days_base = DaysBase(
            on_monday=True,
            on_tuesday=True,
            on_wednesday=True,
            on_thursday=True,
            on_friday=True,
            on_saturday=True,
            on_sunday=True,
        )
        self.assertEqual(days_base.get_week_description(), u'All week')

        days_base = DaysBase(on_monday=True, on_thursday=True, on_friday=True)
        self.assertEqual(days_base.get_week_description(), 'M, Th-F')
        self.assertEqual(
            days_base.get_week_description(verbose=True),
            'Monday, Thursday-Friday'
        )

        days_base = DaysBase(
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=10),
            on_friday=True,
            on_saturday=True,
            on_sunday=True,
            on_monday=True,
            on_wednesday=True,
        )
        self.assertEqual(
            days_base.get_week_description(verbose=True),
            'Wednesdays, Fridays-Mondays'
        )


class AuditionManagerTestCase(TestCase):
    def test_filter_upcoming(self):
        today = timezone.now()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)

        past_audition = AuditionFactory(start_date=yesterday)
        ongoing_audition = AuditionFactory(
            start_date=yesterday,
            end_date=tomorrow
        )
        future_audition = AuditionFactory(start_date=tomorrow)

        upcoming = Audition.objects.filter_upcoming()
        self.assertNotIn(past_audition, upcoming)
        self.assertIn(ongoing_audition, upcoming)
        self.assertIn(future_audition, upcoming)


class AuditionTestCase(TestCase):
    def test_assigned_manager(self):
        self.assertIsInstance(Audition.objects, AuditionManager)

    def test_get_title(self):
        audition = AuditionFactory()
        self.assertEqual(audition.get_title(), u'Auditions')

        audition = AuditionFactory(title='Test Title')
        self.assertEqual(audition.get_title(), u'Test Title')

        audition = AuditionFactory(play=PlayFactory())
        self.assertEqual(
            audition.get_title(),
            u'Auditions for {}'.format(str(audition.play))
        )

        audition = AuditionFactory(
            production_company=ProductionCompanyFactory()
        )
        self.assertEqual(
            audition.get_title(),
            u'Auditions for {}'.format(str(audition.production_company))
        )

        audition = AuditionFactory(
            play=PlayFactory(),
            production_company=ProductionCompanyFactory(),
        )
        self.assertEqual(
            audition.get_title(),
            u'Auditions for {play}, by {company}'.format(
                play=str(audition.play),
                company=str(audition.production_company),
            )
        )

    def test_get_alt_description(self):
        audition = AuditionFactory()
        self.assertEqual(
            audition.get_alt_description(),
            'Auditions on {}.'.format(audition.start_date.strftime('%b %d'))
        )

        audition = AuditionFactory(play=PlayFactory())
        self.assertEqual(
            audition.get_alt_description(),
            'Auditions for a role in {} on {}.'.format(
                str(audition.play),
                audition.start_date.strftime('%b %d'),
            )
        )

        audition = AuditionFactory(
            production_company=ProductionCompanyFactory()
        )
        self.assertEqual(
            audition.get_alt_description(),
            'Auditions with {} on {}.'.format(
                str(audition.production_company),
                audition.start_date.strftime('%b %d'),
            )
        )

        audition = AuditionFactory(end_date=timezone.now() + timedelta(days=1))
        self.assertEqual(
            audition.get_alt_description(),
            'Auditions on {} through {}.'.format(
                audition.start_date.strftime('%b %d'),
                audition.end_date.strftime('%b %d'),
            )
        )

        audition = AuditionFactory(
            play=PlayFactory(),
            production_company=ProductionCompanyFactory(),
            end_date=timezone.now() + timedelta(days=1)
        )
        self.assertEqual(
            audition.get_alt_description(),
            'Auditions for a role in {} with {} on {} through {}.'.format(
                str(audition.play),
                str(audition.production_company),
                audition.start_date.strftime('%b %d'),
                audition.end_date.strftime('%b %d'),
            )
        )

    def test_duration(self):
        audition = AuditionFactory()
        self.assertEqual(
            audition.duration(),
            audition.start_date.strftime('%b. %d')
        )

        audition = AuditionFactory()
        self.assertEqual(
            audition.duration(date_format='%y'),
            audition.start_date.strftime('%y')
        )

        audition = AuditionFactory(end_date=timezone.now() + timedelta(days=1))
        self.assertEqual(
            audition.duration(),
            '{} - {}'.format(
                audition.start_date.strftime('%b. %d'),
                audition.end_date.strftime('%b. %d'),
            )
        )

        audition = AuditionFactory(
            start_date=timezone.now() - timedelta(days=365),
            end_date=timezone.now() - timedelta(days=364)
        )
        self.assertEqual(
            audition.duration(),
            '{} - {} ({})'.format(
                audition.start_date.strftime('%b. %d'),
                audition.end_date.strftime('%b. %d'),
                audition.start_date.year
            )
        )

        audition = AuditionFactory(
            start_date=timezone.now() - timedelta(days=365)
        )
        self.assertEqual(
            audition.duration(date_format='%Y'),
            str(audition.start_date.year)
        )

    def test_save(self):
        audition = AuditionFactory(pk=None, title=None, slug=None)
        with patch('django.db.models.Model.save') as mock_save:
            audition.save()
        mock_save.assert_called_once_with()
        self.assertEqual(audition.title, audition.get_title())
        self.assertEqual(audition.slug, audition.get_slug())

    def test_get_slug(self):
        audition = AuditionFactory()
        self.assertEqual(
            audition.get_slug(),
            slugify(unicode(audition.get_title()))[:47]
        )
        audition_2 = AuditionFactory()
        self.assertEqual(
            audition_2.get_slug(),
            '{}1'.format(slugify(unicode(audition.get_title()))[:47])
        )

    def test_get_absolute_url(self):
        audition = AuditionFactory()
        self.assertIsInstance(audition.get_absolute_url(), unicode)

    def test_unicode(self):
        audition = AuditionFactory()
        self.assertEqual(audition.__unicode__(), unicode(audition.get_title()))


class ProductionCompanyManagerTestCase(TestCase):
    def test_filter_active(self):
        eight_months_ago = timezone.now() - timedelta(days=8*365/12)
        two_years_ago = timezone.now() - timedelta(days=365*2)

        # create company with a recent production
        active_production_company = ProductionCompanyFactory()
        ProductionFactory(
            production_company=active_production_company,
            start_date=eight_months_ago
        )

        # create company with a recent audition
        active_audition_company = ProductionCompanyFactory()
        AuditionFactory(
            production_company=active_audition_company,
            start_date=eight_months_ago
        )

        # create company with an old production
        inactive_production_company = ProductionCompanyFactory()
        ProductionFactory(
            production_company=inactive_production_company,
            start_date=two_years_ago
        )

        # create_company with an old audition
        inactive_audition_company = ProductionCompanyFactory()
        AuditionFactory(
            production_company=inactive_audition_company,
            start_date=two_years_ago
        )

        # create completely inactive company
        inactive_company = ProductionCompanyFactory()

        active_companies = ProductionCompany.objects.filter_active()
        self.assertIn(active_production_company, active_companies)
        self.assertIn(active_audition_company, active_companies)
        self.assertNotIn(inactive_production_company, active_companies)
        self.assertNotIn(inactive_audition_company, active_companies)
        self.assertNotIn(inactive_company, active_companies)


class ProductionCompanyTestCase(TestCase):
    def setUp(self):
        self.company = ProductionCompanyFactory()

    def test_review_set(self):
        production = ProductionFactory(production_company=self.company)
        review = ReviewFactory(production=production)
        self.assertIn(review, self.company.review_set)

    def test_get_related_news(self):
        production = ProductionFactory(production_company=self.company)
        production_news = ArtsNewsFactory(related_production=production)
        company_news = ArtsNewsFactory(related_company=self.company)

        related_news = self.company.get_related_news()
        self.assertIn(production_news, related_news)
        self.assertIn(company_news, related_news)

    def test_published_reviews(self):
        production_1 = ProductionFactory(production_company=self.company)
        production_2 = ProductionFactory(production_company=self.company)
        published_review = ReviewFactory(
            production=production_1,
            is_published=True
        )
        unpublished_review = ReviewFactory(
            production=production_2,
            is_published=False
        )

        published_reviews = self.company.published_reviews()
        self.assertIn(published_review, published_reviews)
        self.assertNotIn(unpublished_review, published_reviews)

    def test_get_absolute_url(self):
        self.assertIsInstance(self.company.get_absolute_url(), unicode)

    def test_unicode(self):
        self.assertEqual(
            self.company.__unicode__(),
            unicode(self.company.name)
        )


class ProductionManagerTestCase(TestCase):
    def test_filter_in_range(self):
        range_start = timezone.now()
        range_end = range_start + timedelta(days=5)

        past_full = ProductionFactory(
            start_date=range_start-timedelta(days=5),
            end_date=range_start-timedelta(days=3)
        )
        past_short = ProductionFactory(
            start_date=range_start-timedelta(days=2)
        )

        future_full = ProductionFactory(
            start_date=range_end+timedelta(days=3),
            end_date=range_end+timedelta(days=5)
        )
        future_short = ProductionFactory(
            start_date=range_end+timedelta(days=2)
        )

        current_short = ProductionFactory(
            start_date=range_start+timedelta(days=1)
        )
        current_within = ProductionFactory(
            start_date=range_start+timedelta(days=1),
            end_date=range_end-timedelta(days=1)
        )
        current_cover = ProductionFactory(
            start_date=range_start-timedelta(days=1),
            end_date=range_end+timedelta(days=1)
        )
        current_overlap_start = ProductionFactory(
            start_date=range_start-timedelta(days=1),
            end_date=range_start+timedelta(days=1)
        )
        current_overlap_end = ProductionFactory(
            start_date=range_end-timedelta(days=1),
            end_date=range_end+timedelta(days=1)
        )

        in_range = Production.objects.filter_in_range(range_start, range_end)
        self.assertNotIn(past_full, in_range)
        self.assertNotIn(past_short, in_range)
        self.assertNotIn(future_full, in_range)
        self.assertNotIn(future_short, in_range)
        self.assertIn(current_short, in_range)
        self.assertIn(current_within, in_range)
        self.assertIn(current_cover, in_range)
        self.assertIn(current_overlap_start, in_range)
        self.assertIn(current_overlap_end, in_range)

    def test_filter_current(self):
        today = timezone.now()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)

        past = ProductionFactory(start_date=yesterday)
        future = ProductionFactory(start_date=yesterday)
        current_short = ProductionFactory(start_date=today)
        current_long = ProductionFactory(
            start_date=yesterday,
            end_date=tomorrow
        )

        current_productions = Production.objects.filter_current()
        self.assertNotIn(past, current_productions)
        self.assertNotIn(future, current_productions)
        self.assertIn(current_short, current_productions)
        self.assertIn(current_long, current_productions)


class ProductionTestCase(TestCase):
    def test_title(self):
        production = ProductionFactory()
        self.assertEqual(production.title, unicode(production.play))

        company = ProductionCompanyFactory()
        production = ProductionFactory(production_company=company)
        self.assertEqual(
            production.title,
            u'{} by {}'.format(production.play, production.production_company)
        )

    def test_save(self):
        production = ProductionFactory(pk=None, slug=None)
        with patch('django.db.models.Model.save') as mock_save:
            production.save()
        self.assertEqual(production.slug, production.get_slug())
        mock_save.assert_called_once_with()

    def test_duration(self):
        production = ProductionFactory()
        self.assertEqual(
            production.duration(),
            production.start_date.strftime('%b. %d')
        )
        self.assertEqual(
            production.duration(append_year=True),
            '{}, {}'.format(
                production.start_date.strftime('%b. %d'),
                str(production.start_date.year)
            )
        )

        production = ProductionFactory(
            end_date=timezone.now() + timedelta(days=1)
        )
        self.assertEqual(
            production.duration(),
            '{} - {}'.format(
                production.start_date.strftime('%b. %d'),
                production.end_date.strftime('%b. %d'),
            )
        )
        self.assertEqual(
            production.duration(conjuction='=+='),
            '{} =+= {}'.format(
                production.start_date.strftime('%b. %d'),
                production.end_date.strftime('%b. %d'),
            )
        )

        production = ProductionFactory(
            start_date=timezone.now() - timedelta(days=365),
            end_date=timezone.now() - timedelta(days=364)
        )
        self.assertEqual(
            production.duration(date_format='%b'),
            '{} - {}, {}'.format(
                production.start_date.strftime('%b'),
                production.end_date.strftime('%b'),
                str(production.start_date.year)
            )
        )
        self.assertEqual(
            production.duration(date_format='%Y'),
            '{} - {}'.format(
                production.start_date.strftime('%Y'),
                production.end_date.strftime('%Y'),
            )
        )

    def test_semi_detailed_duration(self):
        production = ProductionFactory()
        with patch.object(
            production,
            'duration',
            return_value='mock_duration'
        ) as mock_duration:
            duration = production.semi_detailed_duration()
        mock_duration.assert_called_once_with(
            date_format='%B %d',
            append_year=True
        )
        self.assertEqual(duration, 'mock_duration')

    def test_detailed_duration(self):
        production = ProductionFactory()
        with patch.object(
            production,
            'duration',
            return_value='mock_duration'
        ) as mock_duration:
            duration = production.detailed_duration()
        mock_duration.assert_called_once_with(date_format='%B %d, %Y')
        self.assertEqual(duration, 'mock_duration')

    def test_published_reviews(self):
        production = ProductionFactory()
        published_review = ReviewFactory(
            production=production,
            is_published=True
        )
        unpublished_review = ReviewFactory(
            production=production,
            is_published=False
        )

        published_reviews = production.published_reviews()
        self.assertIn(published_review, published_reviews)
        self.assertNotIn(unpublished_review, published_reviews)

    def test_get_slug(self):
        company = ProductionCompanyFactory(name='Company Name')
        production = ProductionFactory(
            start_date=datetime(2017, 1, 3),
            play__title='Test Play Title',
            production_company=company,
        )
        self.assertEqual(
            production.get_slug(),
            '20170103-test-play-title-by-company-name'
        )

    def test_get_absolute_url(self):
        production = ProductionFactory()
        self.assertIsInstance(production.get_absolute_url(), unicode)

    def test_unicode(self):
        production = ProductionFactory()
        self.assertEqual(production.__unicode__(), unicode(production.title))


class PlayTestCase(TestCase):
    def test_unicode(self):
        play = PlayFactory()
        self.assertEqual(play.__unicode__(), unicode(play.title))


class VenueManagerTestCase(TestCase):
    def test_filter_cities(self):
        city1 = 'Austin'
        city2 = 'San Antonio'
        venue1 = VenueFactory(address=AddressFactory(city=city1))
        venue2 = VenueFactory(address=AddressFactory(city=city2))

        by_city = Venue.objects.filter_cities()
        self.assertIn(city1, by_city)
        self.assertIn(city2, by_city)
        self.assertIn(venue1, by_city.get(city1))
        self.assertIn(venue2, by_city.get(city2))

    def test_filter_active(self):
        active_venue = VenueFactory()
        inactive_venue = VenueFactory()
        empty_venue = VenueFactory()

        now = timezone.now()
        two_years_ago = now - timedelta(days=364*2)
        ProductionFactory(start_date=two_years_ago, venue=inactive_venue)
        ProductionFactory(start_date=now, venue=active_venue)

        active_venues = Venue.objects.filter_active()
        self.assertIn(active_venue, active_venues)
        self.assertNotIn(inactive_venue, active_venues)
        self.assertNotIn(empty_venue, active_venues)


class VenueTestCase(TestCase):
    def test_unicode(self):
        venue = VenueFactory()
        self.assertEqual(venue.__unicode__(), unicode(venue.name))


class AddressTestCase(TestCase):
    def test_unicode(self):
        address = AddressFactory()
        self.assertEqual(
            address.__unicode__(),
            '{}, {} TX, {}'.format(
                address.line_1,
                address.city,
                address.zip_code
            )
        )
        address = AddressFactory(line_2='Suite 32')
        self.assertEqual(
            address.__unicode__(),
            '{}, {}, {} TX, {}'.format(
                address.line_1,
                address.line_2,
                address.city,
                address.zip_code
            )
        )


class ArtsNewsManagerTestCase(TestCase):
    def test_filter_media(self):
        video_news = ArtsNewsFactory(video_embed='<iframe />')
        slideshow_news = NewsSlideshowImageFactory().news
        basic_news = ArtsNewsFactory()

        media_news = ArtsNews.objects.filter_media()
        self.assertIn(video_news, media_news)
        self.assertIn(slideshow_news, media_news)
        self.assertNotIn(basic_news, media_news)


class ArtsNewsTestCase(TestCase):
    def test_has_media(self):
        news = ArtsNewsFactory()
        self.assertFalse(news.has_media())

        NewsSlideshowImageFactory(news=news)
        self.assertTrue(news.has_media())

        news = ArtsNewsFactory(video_embed='<iframe src="" />')
        self.assertTrue(news.has_media())

    def test_save(self):
        news = ArtsNewsFactory(pk=None, slug=None)
        with patch('django.db.models.Model.save') as mock_save:
            news.save()
        self.assertEqual(news.slug, news.get_slug())
        mock_save.assert_called_once_with()

    def test_get_slug(self):
        news = ArtsNewsFactory()
        self.assertEqual(news.slug, slugify(unicode(news.title))[:47])
        news_2 = ArtsNewsFactory()
        self.assertEqual(
            news_2.slug,
            '{}1'.format(slugify(unicode(news_2.title))[:47])
        )

    def test_get_absolute_url(self):
        news = ArtsNewsFactory(external_url='http://www.google.com/')
        self.assertEqual(news.get_absolute_url(), news.external_url)
        news = ArtsNewsFactory(external_url=None)
        self.assertIsInstance(news.get_absolute_url(), unicode)

    def test_unicode(self):
        news = ArtsNewsFactory(title='Short Title')
        self.assertEqual(
            news.__unicode__(),
            u'{}: {}'.format(
                news.created_on.strftime('%m/%d/%y'),
                news.title
            )
        )

        news = ArtsNewsFactory(title='This is a very long news title')
        self.assertEqual(
            news.__unicode__(),
            u'{}: {}...'.format(
                news.created_on.strftime('%m/%d/%y'),
                news.title[:20]
            )
        )


class ReviewerManagerTestCase(TestCase):
    def setUp(self):
        self.active_reviewer = ReviewerFactory()
        self.inactive_reviewer = ReviewerFactory()
        six_months_ago = timezone.now() - timedelta(days=6*365/12)
        ReviewFactory(
            is_published=True,
            reviewer=self.active_reviewer,
            published_on=six_months_ago + timedelta(days=40)
        )
        ReviewFactory(
            is_published=True,
            reviewer=self.inactive_reviewer,
            published_on=six_months_ago - timedelta(days=40)
        )

    def test_filter_active(self):
        active = Reviewer.objects.filter_active()
        self.assertIn(self.active_reviewer, active)
        self.assertNotIn(self.inactive_reviewer, active)

    def test_filter_inactive(self):
        active = Reviewer.objects.filter_inactive()
        self.assertIn(self.inactive_reviewer, active)
        self.assertNotIn(self.active_reviewer, active)


class ReviewerTestCase(TestCase):
    def test_full_name(self):
        reviewer = ReviewerFactory(first_name='Jane', last_name='Doe')
        self.assertEqual(reviewer.full_name, 'Jane Doe')

    def test_review_account(self):
        reviewer = ReviewerFactory()
        self.assertEqual(reviewer.review_count, 0)
        ReviewFactory(reviewer=reviewer)
        self.assertEqual(reviewer.review_count, 1)

    def test_unicode(self):
        reviewer = ReviewerFactory()
        self.assertEqual(reviewer.__unicode__(), unicode(reviewer.full_name))


class ExternalReviewTestCase(TestCase):
    def test_unicode(self):
        review = ExternalReviewFactory()
        self.assertEqual(
            review.__unicode__(),
            u"{}'s review of {}".format(review.source_name, review.production)
        )


class SlideshowImageTestCase(TestCase):
    def test_unicode(self):
        image = SlideshowImage(image='image')
        self.assertEqual(image.__unicode__(), unicode(image.image))
