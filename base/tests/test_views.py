from django.test import TestCase, Client
from datetime import timedelta
from django.core.urlresolvers import reverse
from django.utils import timezone

from base.tests import (make_review, make_audition, make_play, make_address,
    make_production_company, make_production, make_venue, make_news,
    make_news_slideshow_image, make_reviewer)

class BaseViewTestCase(TestCase):
    """Base TestCase class with available test client"""
    @classmethod
    def setUpClass(cls):
        cls.client = Client()


class TemplateViewTests(BaseViewTestCase):
    """Unit tests on template views not associated with a single model"""

    def test_principles_view(self):
        """Test 'Principles & Services' page"""
        url = reverse('principles_and_services')
        response = self.client.get(url)
        self.assertIn('html', response.content)

    def test_about_view(self):
        """Test main 'About' page"""
        url = reverse('about')
        response = self.client.get(url)
        self.assertIn('html', response.content)

    def test_homepage(self):
        """Test homepage"""
        review = make_review(cover_image='foobar')
        review.publish()
        news = make_news()
        production = make_production(
            start_date=timezone.now()-timedelta(days=1),
            end_date=timezone.now()+timedelta(days=1),
            poster='foo/bar.baz')
        no_poster_production = make_production(
            start_date=timezone.now())

        url = reverse('home')
        response = self.client.get(url)
        self.assertIn(review.title, response.content)
        self.assertIn(news.title, response.content)
        self.assertIn(production.play.title, response.content)
        self.assertNotIn(no_poster_production.play.title, response.content)


class ReviewerViewTests(BaseViewTestCase):
    """Unit tests for Reviewer-based views"""

    @classmethod
    def setUpClass(cls):
        cls.reviewer1 = make_reviewer()
        cls.reviewer2 = make_reviewer()

    def test_reviewer_list(self):
        """Test 'Reviewers' page"""
        url = reverse('reviewers')
        response = self.client.get(url)
        self.assertIn(self.reviewer1.full_name, response.content)
        self.assertIn(self.reviewer2.full_name, response.content)


class VenueViewTests(BaseViewTestCase):
    """Unit tests for Venue-based views"""

    @classmethod
    def setUpClass(cls):
        cls.venue1 = make_venue(slug='venue1')
        cls.venue2 = make_venue(slug='venue2')

    def test_venue_list(self):
        """Test 'Venues' list page"""
        production = make_production(venue=self.venue1)
        url = reverse('venues')
        response = self.client.get(url)
        self.assertIn(self.venue1.name, response.content)
        self.assertNotIn(self.venue2.name, response.content)

    def test_venue_production_list(self):
        """Test 'Venue Productions' page"""
        production = make_production(venue=self.venue1)
        url = reverse('venue_productions', kwargs={'slug':self.venue1.slug})
        response = self.client.get(url)
        self.assertIn(production.title, response.content)
        self.assertIn(self.venue1.name, response.content)


class CompanyViewTests(BaseViewTestCase):
    """Unit tests for Company-based views"""

    @classmethod
    def setUpClass(cls):
        cls.company1 = make_production_company(slug='company1')
        cls.company2 = make_production_company(slug='company2')
        cls.company3 = make_production_company(slug='company3')

    def test_company_list(self):
        """Test 'Local Theatres' page"""
        make_production(production_company=self.company1)
        make_audition(production_company=self.company2)
        url = reverse('local_theatres')
        response = self.client.get(url)
        self.assertIn(self.company1.name, response.content)
        self.assertIn(self.company2.name, response.content)
        self.assertNotIn(self.company3.name, response.content)

    def test_company_detail(self):
        """Test ProductionCompany detail page"""
        url = reverse('production_company', kwargs={'slug':self.company1.slug})
        response = self.client.get(url)
        self.assertIn(self.company1.name, response.content)
        self.assertNotIn(self.company2.name, response.content)

    def test_company_production_list(self):
        """Test Company Productions list page"""
        production1 = make_production(production_company=self.company1)
        url = reverse('company_productions', kwargs={'slug':self.company1.slug})
        response = self.client.get(url)
        self.assertIn(production1.play.title, response.content)
        self.assertIn(self.company1.name, response.content)

    def test_company_review_list(self):
        """Test Company Review list page"""
        production1 = make_production(production_company=self.company1)
        review1 = make_review(production=production1)
        review1.publish()
        url = reverse('company_reviews', kwargs={'slug':self.company1.slug})
        response = self.client.get(url)
        self.assertIn(review1.production.play.title, response.content)
        self.assertIn(production1.title, response.content)
        self.assertIn(self.company1.name, response.content)

    def test_company_audition_list(self):
        """Test Company Audition list page"""
        audition1 = make_audition(production_company=self.company1)
        url = reverse('company_auditions', kwargs={'slug':self.company1.slug})
        response = self.client.get(url)
        self.assertIn(audition1.title, response.content)
        self.assertIn(self.company1.name, response.content)


class ProductionViewTests(BaseViewTestCase):
    """Unit tests for Production-based views"""

    @classmethod
    def setUpClass(cls):
        cls.production1 = make_production(description='foobar baz')
        cls.production2 = make_production(description='lorem ipsum')
        cls.production3 = make_production(description='dolor sit amet')

    def test_production_detail_view(self):
        """Test Production detail page"""
        url = reverse('production_detail',
            kwargs={'slug':self.production1.slug})
        response = self.client.get(url)
        self.assertIn(self.production1.title, response.content)
        self.assertIn(self.production1.venue.name, response.content)
        self.assertNotIn(self.production2.description, response.content)

    def test_upcoming_production_view(self):
        """Test Upcoming Productions page"""
        current_production = make_production(
            start_date=timezone.now()+timedelta(days=1))
        previous_production = make_production(
            start_date=timezone.now()-timedelta(days=1))
        url = reverse('productions_upcoming')
        response = self.client.get(url)
        self.assertIn(current_production.title, response.content)
        self.assertNotIn(previous_production.title, response.content)

    def test_weekly_production_view(self):
        """Test Productions by Week page"""
        start_date = timezone.now()
        current_production = make_production(
            start_date=start_date+timedelta(days=1))
        previous_production = make_production(
            start_date=start_date-timedelta(days=1))
        url = reverse('productions_weekly',
            kwargs={'start_date':start_date.strftime('%Y%m%d')})
        response = self.client.get(url)
        self.assertIn(current_production.title, response.content)
        self.assertNotIn(previous_production.title, response.content)

    def test_monthly_production_view(self):
        """Test Productions by Month page"""
        start_date = timezone.now()
        current_production = make_production(start_date=start_date)
        previous_production = make_production(
            start_date=start_date-timedelta(days=50))
        future_production = make_production(
            start_date=start_date+timedelta(days=50))
        url = reverse('productions_monthly', kwargs={
            'year':start_date.strftime('%Y'),
            'month':start_date.strftime('%m')})
        response = self.client.get(url)
        self.assertIn(current_production.title, response.content)
        self.assertNotIn(previous_production.title, response.content)
        self.assertNotIn(future_production.title, response.content)

    def test_city_production_view(self):
        """Test Productions by City view"""
        city = 'Austin'
        city_venue = make_venue(address=make_address(city=city))
        other_venue = make_venue(address=make_address(city='Foobar'))
        city_production = make_production(venue=city_venue)
        other_production = make_production(venue=other_venue)

        url = reverse('productions_city', kwargs={'city':city})
        response = self.client.get(url)
        self.assertIn(city, response.content)

        url = reverse('productions_city', kwargs={'city':city})
        response = self.client.get(url)
        self.assertIn(city_production.title, response.content)
        self.assertNotIn(other_production.title, response.content)


class NewsViewTests(BaseViewTestCase):
    """Unit tests for ArtsNews-based views"""

    @classmethod
    def setUpClass(cls):
        cls.news1 = make_news(content='foobarbaz')
        cls.news2 = make_news(content='lorem ipsum')
        cls.news3 = make_news(content='dolor sit amet')

    def test_news_list_view(self):
        """Test ArtsNews list page"""
        url = reverse('news_list')
        response = self.client.get(url)
        self.assertIn(self.news1.title, response.content)
        self.assertIn(self.news2.title, response.content)
        self.assertIn(self.news3.title, response.content)

    def test_news_detail_view(self):
        """Test ArtsNews detail page"""
        url = reverse('news_detail', kwargs={'slug':self.news1.slug})
        response = self.client.get(url)
        self.assertIn(self.news1.title, response.content)
        self.assertNotIn(self.news2.content, response.content)


class AuditionViewTests(BaseViewTestCase):
    """Unit tests for Audition-based views"""

    @classmethod
    def setUpClass(cls):
        cls.audition1 = make_audition(title='Title 1', content='foobar')
        cls.audition2 = make_audition(title='Title 2', content='baz')

    def audition_detail_view(self):
        """Test Audition detail page"""
        url = reverse('audition_detail', kwargs={'slug':self.audition1.slug})
        response = self.client.get(url)
        self.assertIn(self.audition1.get_title(), response.content)
        self.assertIn(self.audition1.content, response.content)
        self.assertNotIn(self.audition2.get_title(), response.content)
        self.assertNotIn(self.audition2.content, response.content)

    def audition_list_view(self):
        """Test Audition list page"""
        url = reverse('auditions')
        response = self.client.get(url)
        self.assertIn(self.audition1.get_title(), response.content)
        self.assertIn(self.audition2.get_title(), response.content)


class ReviewViewTests(BaseViewTestCase):
    """Unit tests for Review-based views"""

    @classmethod
    def setUpClass(cls):
        cls.review1 = make_review(title='Review 1')
        cls.review2 = make_review(title='Review 2')

    def review_list(self):
        """Test Review list page"""
        url = reverse('reviews')
        response = self.client.get(url)
        self.assertIn(self.review1.title, response.content)
        self.assertIn(self.review2.title, response.content)

    def review_detail_view(self):
        """Test Review detail page"""
        url = reverse('reviews', kwargs={'slug':self.review1.slug})
        response = self.client.get(url)
        self.assertIn(self.review1.title, response.content)
        self.assertIn(self.review1.content, response.content)
        self.assertNotIn(self.review2.title, response.content)
