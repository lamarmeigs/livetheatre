from django.test import TestCase
from datetime import timedelta
from django.utils import timezone

from base.models import (Audition, Production, Reviewer, Venue, ArtsNews, 
    ProductionCompany)
from base.tests import (make_review, make_audition, make_play, make_address,
    make_production_company, make_production, make_venue, make_news,
    make_news_slideshow_image, make_reviewer)

class ReviewTests(TestCase):
    """Test methods in Review model class"""

    def test_get_title(self):
        """Test retrieving titles from connected production"""
        untitled_review = make_review()
        self.assertEqual(
            untitled_review.get_title(),
            'Review: %s' % untitled_review.production)

        titled_review = make_review(title='Test Review')
        self.assertEqual(untitled_review.title, untitled_review.get_title())

    def test_get_slug(self):
        """Test crafting slugs from titles"""
        review1 = make_review(title='Indexed Review'); review1.save()
        review2 = make_review(title='Indexed Review'); review2.save()
        review3 = make_review(title='Indexed Review'); review3.save()
        self.assertNotEqual(review1.slug, review2.slug)
        self.assertNotEqual(review2.slug, review3.slug)
        self.assertTrue(review2.slug.endswith('1'))
        self.assertTrue(review3.slug.endswith('2'))

    def test_publishing(self):
        """Test publish and unpublish methods"""
        review = make_review()
        review.publish()
        self.assertTrue(review.is_published)
        self.assertIsNotNone(review.published_on)
        review.unpublish()
        self.assertFalse(review.is_published)

    def test_save(self):
        """Test overridden save method"""
        review = make_review(slug='bad-slug')
        review.save()
        self.assertEqual(review.title, review.get_title())
        self.assertEqual(review.slug, review.get_slug())
        self.assertNotEqual(review.slug, 'bad-slug')

    def test_get_absolute_url(self):
        """Test getting this review's url"""
        review = make_review()
        self.assertIn(review.slug, review.get_absolute_url())


class AuditionManagerTests(TestCase):
    """Test methods in AuditionManager class"""
    def test_filter_upcoming(self):
        """Test finding ongoing or upcoming auditions"""
        today = timezone.now()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)

        past_audition = make_audition(start_date=yesterday)
        ongoing_audition = make_audition(
            start_date=yesterday, end_date=tomorrow)
        future_audition = make_audition(start_date=tomorrow)

        upcoming = Audition.objects.filter_upcoming()
        self.assertNotIn(past_audition, upcoming)
        self.assertIn(ongoing_audition, upcoming)
        self.assertIn(future_audition, upcoming)


class AuditionTests(TestCase):
    """Test methods in Audition model class"""

    def test_get_title(self):
        """Test crafting a title from connected objects"""
        titled_audition = make_audition(title='Test Title')
        self.assertEqual(titled_audition.title, titled_audition.get_title())

        play = make_play()
        company = make_production_company()
        play_company_audition = make_audition(play=play, 
            production_company=company)
        self.assertIn(play.title, play_company_audition.get_title())
        self.assertIn(company.name, play_company_audition.get_title())

        play_audition = make_audition(play=play)
        self.assertIn(play.title, play_audition.get_title())

        company_audition = make_audition(production_company=company)
        self.assertIn(company.name, company_audition.get_title())

        empty_audition = make_audition()
        self.assertEqual(empty_audition.get_title(), 'Audition')

    def test_get_alt_description(self):
        """Test crafting an alternate description"""
        play = make_play()
        company = make_production_company()
        start_date = timezone.now()
        end_date = start_date + timedelta(days=1)
        audition = make_audition(play=play, production_company=company,
            start_date=start_date, end_date=end_date)

        alt_description = audition.get_alt_description()
        self.assertIn(play.title, alt_description)
        self.assertIn(company.name, alt_description)
        self.assertIn(start_date.strftime('%b %d'), alt_description)
        self.assertIn(end_date.strftime('%b %d'), alt_description)

    def test_duration(self):
        """Test creating the display of an Audition object's duration"""
        start_date = timezone.now() - timedelta(days=365)
        end_date = start_date + timedelta(days=1)
        date_fmt = '%b %d'
        audition = make_audition(start_date=start_date, end_date=end_date)
        duration = audition.duration(date_fmt)
        self.assertIn(start_date.strftime(date_fmt), duration)
        self.assertIn(end_date.strftime('%b %d'), duration)
        self.assertIn(str(start_date.year), duration)

    def test_save(self):
        """Test overridden save method"""
        audition = make_audition(slug='bad-slug')
        audition.save()
        self.assertEqual(audition.title, audition.get_title())
        self.assertEqual(audition.slug, audition.get_slug())
        self.assertNotEqual(audition.slug, 'bad-slug')

    def test_get_slug(self):
        """Test building an Audition object's slug"""
        audition1 = make_audition(title='Indexed Audition'); audition1.save()
        audition2 = make_audition(title='Indexed Audition'); audition2.save()
        audition3 = make_audition(title='Indexed Audition'); audition3.save()
        self.assertNotEqual(audition1.slug, audition2.slug)
        self.assertNotEqual(audition2.slug, audition3.slug)
        self.assertTrue(audition2.slug.endswith('1'))
        self.assertTrue(audition3.slug.endswith('2'))

    def test_get_absolute_url(self):
        """Test returning an Audition object's url"""
        audition = make_audition()
        self.assertIn(audition.slug, audition.get_absolute_url())


class ProductionCompanyManagerTests(TestCase):
    """Test the methods on ProductionCompanyManager class"""
    def test_filter_active(self):
        """Test returning only active companies"""
        eight_months_ago = timezone.now() - timedelta(days=8*365/12)
        two_years_ago = timezone.now() - timedelta(days=365*2)

        # create company with a recent production
        active_production_company = make_production_company()
        make_production(production_company=active_production_company,
            start_date=eight_months_ago)

        # create company with a recent audition
        active_audition_company = make_production_company()
        make_audition(production_company=active_audition_company,
            start_date=eight_months_ago)

        # create company with an old production
        inactive_production_company = make_production_company()
        make_production(production_company=inactive_production_company,
            start_date=two_years_ago)

        # create_company with an old audition
        inactive_audition_company = make_production_company()
        make_audition(production_company=inactive_audition_company,
            start_date=two_years_ago)

        # create completely inactive company
        inactive_company = make_production_company()

        active_companies = ProductionCompany.objects.filter_active()
        self.assertIn(active_production_company, active_companies)
        self.assertIn(active_audition_company, active_companies)
        self.assertNotIn(inactive_production_company, active_companies)
        self.assertNotIn(inactive_audition_company, active_companies)
        self.assertNotIn(inactive_company, active_companies)


class ProductionCompanyTests(TestCase):
    """Test the methods and properties of ProductionCompany model class"""

    def test_review_set(self):
        """Test retrieving reviews for this company's productions"""
        company = make_production_company()
        production = make_production(production_company=company)
        review = make_review(production=production)
        review2 = make_review()

        review_set = company.review_set.all()
        self.assertIn(review, review_set)
        self.assertNotIn(review2, review_set)

    def test_get_related_news(self):
        """Test retrieving news related to a company and its productions"""
        company = make_production_company()
        production = make_production(production_company=company)
        company_news = make_news(related_company=company)
        production_news = make_news(related_production=production)
        both_news = make_news(related_company=company,
            related_production=production)

        related_news = company.get_related_news()
        self.assertIn(company_news, related_news)
        self.assertIn(production_news, related_news)
        self.assertIn(both_news, related_news)
        self.assertEqual(related_news.count(), 3)

    def test_get_absolute_url(self):
        """Test returning a ProductionCompany object's url"""
        company = make_production_company(slug='test-company')
        self.assertIn(company.slug, company.get_absolute_url())


class ProductionManagerTests(TestCase):
    """Test the methods on the ProductionManager class"""

    def test_filter_in_range(self):
        """Test retrieving productions in a range"""
        range_start = timezone.now()
        range_end = range_start + timedelta(days=5)

        past_full = make_production(
            start_date=range_start-timedelta(days=5),
            end_date=range_start-timedelta(days=3))
        past_short = make_production(start_date=range_start-timedelta(days=2))

        future_full = make_production(
            start_date=range_end+timedelta(days=3),
            end_date=range_end+timedelta(days=5))
        future_short = make_production(start_date=range_end+timedelta(days=2))

        current_short = make_production(
            start_date=range_start+timedelta(days=1))
        current_within = make_production(
            start_date=range_start+timedelta(days=1),
            end_date=range_end-timedelta(days=1))
        current_cover = make_production(
            start_date=range_start-timedelta(days=1),
            end_date=range_end+timedelta(days=1))
        current_overlap_start = make_production(
            start_date=range_start-timedelta(days=1),
            end_date=range_start+timedelta(days=1))
        current_overlap_end = make_production(
            start_date=range_end-timedelta(days=1),
            end_date=range_end+timedelta(days=1))

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

    def filter_current(self):
        """Test filtering current productions"""
        today = timezone.now()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)

        past = make_production(start_date=yesterday)
        future = make_production(start_date=yesterday)
        current_short = make_production(start_date=today)
        current_long = make_production(start_date=yesterday, end_date=tomorrow)

        current_productions = Production.objects.filter_current()
        self.assertNotIn(past, current_productions)
        self.assertNotIn(future, current_productions)
        self.assertIn(current_short, current_productions)
        self.assertIn(current_long, current_productions)


class ProductionTests(TestCase):
    """Test methods on the Production model class"""

    def test_title(self):
        """Test crafting the title property from the connected objects"""
        company = make_production_company()
        production = make_production(production_company=company)
        self.assertIn(production.play.title, production.title)
        self.assertIn(production.production_company.name, production.title)

    def test_save(self):
        """Test overridden save method"""
        production = make_production(slug='bad-slug')
        production.save()
        self.assertEqual(production.slug, production.get_slug())
        self.assertNotEqual(production.slug, 'bad-slug')

    def test_duration(self):
        """Test crafting display of duration"""
        start_date = timezone.now() - timedelta(days=365)
        end_date = start_date + timedelta(days=1)
        production = make_production(start_date=start_date, end_date=end_date)

        date_fmt = '%b %d'
        duration = production.duration(date_format=date_fmt)
        self.assertIn(start_date.strftime(date_fmt), duration)
        self.assertIn(end_date.strftime(date_fmt), duration)
        self.assertIn(str(start_date.year), duration)

    def test_detailed_duration(self):
        """Test return a semi-detailed duration display"""
        start_date = timezone.now()
        end_date = start_date + timedelta(days=1)
        production = make_production(start_date=start_date, end_date=end_date)

        date_fmt = '%b %d'
        duration = production.duration(date_format=date_fmt)
        self.assertIn(start_date.strftime(date_fmt), duration)
        self.assertIn(end_date.strftime(date_fmt), duration)
        self.assertIn(str(start_date.year), duration)

    def test_detailed_duration(self):
        """Test returned a detailed duration display"""
        start_date = timezone.now() - timedelta(days=365)
        end_date = start_date + timedelta(days=1)
        production = make_production(start_date=start_date, end_date=end_date)

        date_fmt = '%B %d, %Y'
        duration = production.detailed_duration()
        self.assertIn(start_date.strftime(date_fmt), duration)
        self.assertIn(end_date.strftime(date_fmt), duration)

    def test_get_slug(self):
        """Test creating unique slugs for Production objects"""
        play = make_play()
        production1 = make_production(play=play); production1.save()
        production2 = make_production(play=play); production2.save()
        production3 = make_production(play=play); production3.save()
        self.assertNotEqual(production1.slug, production2.slug)
        self.assertNotEqual(production2.slug, production3.slug)
        self.assertTrue(production2.slug.endswith('1'))
        self.assertTrue(production3.slug.endswith('2'))

    def test_get_absolute_url(self):
        """Test return a Production object's url"""
        production = make_production()
        self.assertIn(production.slug, production.get_absolute_url())

    def test_week_booleans(self):
        """Test creating a list of booleans of the days when production runs"""
        production = make_production(on_monday=True, on_wednesday=True,
            on_saturday=True, on_sunday=True)
        self.assertEqual(
            production._week_booleans(),
            [True, False, True, False, False, True, True])

    def test_get_last_sequential_day_index(self):
        """Test returning an index of the last day in a sequence"""
        production = make_production(on_monday=True, on_wednesday=True,
            on_saturday=True, on_sunday=True)
        self.assertEqual(production.get_last_sequential_day_index(), 0)
        self.assertIsNone(production.get_last_sequential_day_index(start_on=1))
        self.assertEqual(
            production.get_last_sequential_day_index(start_on=5, wrap=False), 6)
        self.assertEqual(
            production.get_last_sequential_day_index(start_on=5), 0)

    def test_get_week_description(self):
        """Test returning a string describing the days of the week"""
        no_wrap_production = make_production(on_monday=True, on_wednesday=True,
            on_thursday=True, on_friday=True)
        self.assertEqual(no_wrap_production.get_week_description(), 'M, W-F')
        self.assertEqual(
            no_wrap_production.get_week_description(verbose=True),
            'Monday, Wednesday-Friday')

        wrap_production = make_production(on_monday=True, on_wednesday=True,
            on_saturday=True, on_sunday=True)
        self.assertEqual(wrap_production.get_week_description(), 'W, Sat-M')
        self.assertEqual(
            wrap_production.get_week_description(verbose=True),
            'Wednesday, Saturday-Monday')

        all_week_production = make_production(on_monday=True,
            on_tuesday=True, on_wednesday=True, on_thursday=True,
            on_friday=True, on_saturday=True, on_sunday=True)
        self.assertEqual(all_week_production.get_week_description(), 'All week')

        no_day_production = make_production()
        self.assertEqual(no_day_production.get_week_description(), '')


class VenueManagerTests(TestCase):
    """Test filter methods on VenueManager class"""

    def test_filter_cities(self):
        """Test categorizing Venue objects by their city field"""
        city1 = 'Austin'
        city2 = 'San Antonio'
        venue1 = make_venue(address=make_address(city=city1))
        venue2 = make_venue(address=make_address(city=city2))

        by_city = Venue.objects.filter_cities()
        self.assertIn(city1, by_city)
        self.assertIn(city2, by_city)
        self.assertIn(venue1, by_city.get(city1))
        self.assertIn(venue2, by_city.get(city2))

    def test_filter_active(self):
        """Test returning only active venues"""
        active_venue = make_venue()
        inactive_venue = make_venue()
        empty_venue = make_venue()

        now = timezone.now()
        two_years_ago = now - timedelta(days=364*2)
        make_production(start_date=two_years_ago, venue=inactive_venue)
        make_production(start_date=now, venue=active_venue)

        active_venues = Venue.objects.filter_active()
        self.assertIn(active_venue, active_venues)
        self.assertNotIn(inactive_venue, active_venues)
        self.assertNotIn(empty_venue, active_venues)


class ArtsNewsManagerTests(TestCase):
    """Test methods on ArtsNewsManager class"""

    def test_filter_media(self):
        """Test retrieving only ArtsNews objects with populated media fields"""
        video_news = make_news(video_embed='<iframe />')
        slideshow_news = make_news_slideshow_image().news
        basic_news = make_news()

        media_news = ArtsNews.objects.filter_media()
        self.assertIn(video_news, media_news)
        self.assertIn(slideshow_news, media_news)
        self.assertNotIn(basic_news, media_news)


class ArtsNewsTests(TestCase):
    """Test methods on ArtsNews model class"""

    def test_has_media(self):
        """Test checking for media fields"""
        video_news = make_news(video_embed='<iframe />')
        self.assertTrue(video_news.has_media())

        slideshow_news = make_news_slideshow_image().news
        self.assertTrue(slideshow_news.has_media())

        basic_news = make_news()
        self.assertFalse(basic_news.has_media())

    def test_save(self):
        """Test overridden save method"""
        news = make_news(slug='bad-slug')
        news.save()
        self.assertEqual(news.slug, news.get_slug())
        self.assertNotEqual(news.slug, 'bad-slug')

    def test_get_slug(self):
        """Test creating unique slugs"""
        news1 = make_news(title='Indexed News'); news1.save()
        news2 = make_news(title='Indexed News'); news2.save()
        news3 = make_news(title='Indexed News'); news3.save()
        self.assertNotEqual(news1.slug, news2.slug)
        self.assertNotEqual(news2.slug, news3.slug)
        self.assertTrue(news2.slug.endswith('1'))
        self.assertTrue(news3.slug.endswith('2'))

    def test_get_absolute_url(self):
        """Test returning the url for an ArtsNews object"""
        basic_news = make_news()
        self.assertIn(basic_news.slug, basic_news.get_absolute_url())
        external_url = 'http://www.nytimes.com/'
        external_news = make_news(external_url=external_url)
        self.assertEqual(external_url, external_news.get_absolute_url())


class ReviewerManagerTests(TestCase):
    """Test methods on ReviewerManager class"""

    def test_filter_active(self):
        """Test returning active Reviewer objects"""
        active_reviewer = make_reviewer()
        inactive_reviewer = make_reviewer()
        six_months_ago = timezone.now() - timedelta(days=6*365/12)
        make_review(
            reviewer=active_reviewer, is_published=True,
            published_on=six_months_ago + timedelta(days=40))
        make_review(
            reviewer=inactive_reviewer, is_published=True,
            published_on=six_months_ago - timedelta(days=40))

        active = Reviewer.objects.filter_active()
        self.assertIn(active_reviewer, active)
        self.assertNotIn(inactive_reviewer, active)

    def test_filter_inactive(self):
        """Test returning inactive Reviewer objects"""
        active_reviewer = make_reviewer()
        inactive_reviewer = make_reviewer()
        six_months_ago = timezone.now() - timedelta(days=6*365/12)
        make_review(
            reviewer=active_reviewer, is_published=True,
            published_on=six_months_ago + timedelta(days=40))
        make_review(
            reviewer=inactive_reviewer, is_published=True,
            published_on=six_months_ago - timedelta(days=40))

        active = Reviewer.objects.filter_inactive()
        self.assertIn(inactive_reviewer, active)
        self.assertNotIn(active_reviewer, active)


class ReviewerTests(TestCase):
    """Test methods and properties on Reviewer model classes"""

    def test_full_name(self):
        """Test crafting a Reviewer objects full name"""
        reviewer = make_reviewer()
        self.assertIn(reviewer.first_name, reviewer.full_name)
        self.assertIn(reviewer.last_name, reviewer.full_name)

    def test_review_count(self):
        """Test returning the count of Reviews associated with this Reviewer"""
        reviewer = make_reviewer()
        num_reviews = 2
        for _ in range(num_reviews):
            make_review(reviewer=reviewer)
        self.assertEqual(num_reviews, reviewer.review_count)
