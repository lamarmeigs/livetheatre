from datetime import date, timedelta

from django.http import HttpRequest
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.test import TestCase
from django.utils import timezone
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from mock import patch

from base.forms import ContactForm
from base.models import (
    ArtsNews, Audition, Production, ProductionCompany, Review, Reviewer, Venue
)
from base.views import (
    AboutView, AuditionDetailView, CityPerformanceView,
    CompanyAuditionListView, CompanyReviewListView, CompanyNewsListView,
    CompanyObjectListView, CompanyPastAuditionListView,
    CompanyProductionListView, ContactFormView, ContactThanksView,
    DateRangePerformanceView, HomepageView, LocalTheatresView,
    MonthPerformanceView, NewsDetailView, NewsListView, PastAuditionListView,
    PrinciplesServicesView, ProductionCompanyView, ProductionDetailView,
    ProductionNewsListView, ReviewDetailView, ReviewListView, ReviewerListView,
    UpcomingAuditionListView, UpcomingPerformanceView, VenueListView,
    VenueProductionListView, WeekPerformanceView,
)
from base.tests.fixtures import (
    AddressFactory, ArtsNewsFactory, AuditionFactory,
    NewsSlideshowImageFactory, PlayFactory, ProductionFactory,
    ProductionCompanyFactory, ReviewFactory, ReviewerFactory, VenueFactory
)


class HomepageViewTestCase(TestCase):
    def setUp(self):
        self.view = HomepageView()

    def test_inherits_base_class(self):
        self.assertIsInstance(self.view, TemplateView)

    def test_class_attributes(self):
        self.assertEqual(HomepageView.template_name, 'homepage.html')

    def test_get_context_data(self):
        production = ProductionFactory(poster='poster')
        no_poster_production = ProductionFactory()
        review = ReviewFactory(is_published=True, cover_image='image')
        unpublished_review = ReviewFactory(is_published=False, cover_image='x')
        no_image_review = ReviewFactory(is_published=True)

        context = self.view.get_context_data()
        self.assertIn(production, context['productions'])
        self.assertNotIn(no_poster_production, context['productions'])
        self.assertIn(review, context['reviews'])
        self.assertNotIn(unpublished_review, context['reviews'])
        self.assertNotIn(no_image_review, context['reviews'])
        self.assertIsNone(context['audition_groups'])
        self.assertIsNone(context['media_news'])
        self.assertIsNone(context['news_groups'])

        audition = AuditionFactory()
        media_news = ArtsNewsFactory(video_embed='<iframe />')
        news = ArtsNewsFactory()

        context = self.view.get_context_data()
        self.assertIn([audition], context['audition_groups'])
        self.assertEqual(context['media_news'], media_news)
        self.assertIn([news], context['news_groups'])


class ReviewDetailViewTestCase(TestCase):
    def test_inherits_base_class(self):
        self.assertIsInstance(ReviewDetailView(), DetailView)

    def test_class_attributes(self):
        self.assertEqual(ReviewDetailView.model, Review)
        self.assertEqual(ReviewDetailView.template_name, 'reviews/detail.html')

    def test_get_context_data(self):
        company = ProductionCompanyFactory()
        production = ProductionFactory(production_company=company)
        other_production = ProductionFactory()
        review = ReviewFactory(is_published=True, production=production)
        unpublished_review = ReviewFactory(is_published=False)
        news = ArtsNewsFactory()

        view = ReviewDetailView()
        view.object = review
        with patch.object(view, 'get_object', return_value=review):
            context = view.get_context_data()
        self.assertIn(review, context['recent_reviews'])
        self.assertNotIn(unpublished_review, context['recent_reviews'])
        self.assertNotIn(production, context['company_productions'])
        self.assertNotIn(other_production, context['company_productions'])
        self.assertIn(news, context['recent_news'])

        company_production_2 = ProductionFactory(production_company=company)
        with patch.object(view, 'get_object', return_value=review):
            context = view.get_context_data()
        self.assertIn(company_production_2, context['company_productions'])


class ReviewListViewTestCase(TestCase):
    def test_inherits_base_class(self):
        self.assertIsInstance(ReviewListView(), ListView)

    def test_class_attributes(self):
        self.assertEqual(ReviewListView.model, Review)
        self.assertEqual(ReviewListView.template_name, 'reviews/list.html')

    def test_get_context_data(self):
        request = HttpRequest()
        request.GET = {'page': 2}
        view = ReviewListView(request=request)
        view.object_list = [ReviewFactory()]
        with patch.object(Paginator, 'page') as mock_page:
            view.get_context_data()
        mock_page.assert_called_once_with(2)

        with patch.object(
            Paginator,
            'page',
            side_effect=PageNotAnInteger()
        ) as mock_page:
            try:
                view.get_context_data()
            except PageNotAnInteger:
                pass
        mock_page.has_call(1)

        with patch.object(Paginator, 'page', side_effect=EmptyPage()) as mock:
            try:
                view.get_context_data()
            except EmptyPage:
                pass
        mock.has_call(1)


class ProductionCompanyViewTestCase(TestCase):
    def test_inherits_base_class(self):
        self.assertIsInstance(ProductionCompanyView(), DetailView)

    def test_class_attributes(self):
        self.assertEqual(ProductionCompanyView.model, ProductionCompany)
        self.assertEqual(
            ProductionCompanyView.template_name,
            'companies/detail.html'
        )
        self.assertEqual(
            ProductionCompanyView.context_object_name,
            'company'
        )

    def test_get_context_data(self):
        company = ProductionCompanyFactory()
        view = ProductionCompanyView()
        view.object = company
        with patch.object(company, 'get_related_news', return_value=[1, 2]):
            context = view.get_context_data()
        self.assertEqual(context['related_news'], [1, 2])


class LocalTheatresViewTestCase(TestCase):
    def test_inherits_base_class(self):
        self.assertIsInstance(LocalTheatresView(), ListView)

    def test_class_attributes(self):
        self.assertEqual(LocalTheatresView.model, ProductionCompany)
        self.assertEqual(
            LocalTheatresView.template_name,
            'companies/list.html'
        )
        self.assertEqual(LocalTheatresView.context_object_name, 'companies')

    def test_get_queryset(self):
        company_1 = ProductionCompanyFactory(name='A company')
        company_2 = ProductionCompanyFactory(name='The a different company')
        company_3 = ProductionCompanyFactory(name='b different company')

        view = LocalTheatresView()
        view.queryset = [company_1, company_2, company_3]
        ordered_companies = view.get_queryset()
        self.assertEqual(
            ordered_companies,
            [
                ('A', [company_1, company_2]),
                ('B', [company_3]),
            ]
        )


class AuditionDetailViewTestCase(TestCase):
    def test_inherits_base_class(self):
        self.assertIsInstance(AuditionDetailView(), DetailView)

    def test_class_attributes(self):
        self.assertEqual(AuditionDetailView.model, Audition)
        self.assertEqual(
            AuditionDetailView.template_name,
            'auditions/detail.html'
        )

    def test_get_context_data(self):
        news = ArtsNewsFactory()
        audition = AuditionFactory()
        upcoming_audition = AuditionFactory(
            start_date=timezone.now() + timedelta(days=1)
        )

        view = AuditionDetailView()
        view.object = audition
        with patch.object(
            AuditionDetailView,
            'get_object',
            return_value=audition
        ):
            context = view.get_context_data()
        self.assertIn(upcoming_audition, context['upcoming_auditions'])
        self.assertIn(news, context['recent_news'])
        self.assertEqual(context['company_productions'], [])


class UpcomingAuditionListViewTestCase(TestCase):
    def test_inherits_base_class(self):
        self.assertIsInstance(UpcomingAuditionListView(), ListView)

    def test_class_attributes(self):
        self.assertEqual(UpcomingAuditionListView.model, Audition)
        self.assertEqual(
            UpcomingAuditionListView.template_name,
            'auditions/upcoming_list.html'
        )


class PastAuditionListViewTestCase(TestCase):
    def test_inherits_base_class(self):
        self.assertIsInstance(PastAuditionListView(), ListView)

    def test_class_attributes(self):
        self.assertEqual(PastAuditionListView.model, Audition)
        self.assertEqual(
            PastAuditionListView.template_name,
            'auditions/past_list.html'
        )

    def test_get_queryset(self):
        future_audition = AuditionFactory(
            start_date=timezone.now() + timedelta(days=1)
        )
        audition_1 = AuditionFactory(
            start_date=timezone.now() - timedelta(days=1),
            play=PlayFactory(title='1')
        )
        audition_2 = AuditionFactory(
            start_date=timezone.now() - timedelta(days=2),
            play=PlayFactory(title='2')
        )

        view = PastAuditionListView()
        past_auditions = view.get_queryset()
        self.assertNotIn(future_audition, past_auditions)
        self.assertEqual(past_auditions[0], audition_1)
        self.assertEqual(past_auditions[1], audition_2)

    def test_get_context_data(self):
        request = HttpRequest()
        request.GET = {'page': 2}
        view = PastAuditionListView(request=request)
        view.object_list = [AuditionFactory()]
        with patch.object(Paginator, 'page', return_value='page') as mock_page:
            context = view.get_context_data()
        mock_page.assert_called_once_with(2)
        self.assertEqual(context['page'], 'page')

        with patch.object(
            Paginator,
            'page',
            side_effect=PageNotAnInteger()
        ) as mock_page:
            try:
                view.get_context_data()
            except PageNotAnInteger:
                pass
        mock_page.has_call(1)

        with patch.object(Paginator, 'page', side_effect=EmptyPage()) as mock:
            try:
                view.get_context_data()
            except EmptyPage:
                pass
        mock.has_call(1)


class NewsDetailViewTestCase(TestCase):
    def test_inherits_base_class(self):
        self.assertIsInstance(NewsDetailView(), DetailView)

    def test_class_attributes(self):
        self.assertEqual(NewsDetailView.model, ArtsNews)
        self.assertEqual(NewsDetailView.template_name, 'news/detail.html')
        self.assertEqual(NewsDetailView.context_object_name, 'news')

    def test_get_context_data(self):
        news = ArtsNewsFactory()
        other_news = ArtsNewsFactory()
        review = ReviewFactory()
        production = ProductionFactory()

        view = NewsDetailView()
        view.object = news
        with patch.object(view, 'get_object', return_value=news):
            context = view.get_context_data()
        self.assertIn(review, context['recent_reviews'])
        self.assertIn(other_news, context['recent_news'])
        self.assertNotIn(news, context['recent_news'])
        self.assertIn(production, context['current_productions'])


class NewsListViewTestCase(TestCase):
    def test_inherits_base_class(self):
        self.assertIsInstance(NewsListView(), ListView)

    def test_class_attributes(self):
        self.assertEqual(NewsListView.model, ArtsNews)
        self.assertEqual(NewsListView.template_name, 'news/list.html')

    def test_get_queryset(self):
        external_news = ArtsNewsFactory(external_url='http://www.google.com/')
        video_news = ArtsNewsFactory(video_embed='<iframe />')
        slideshow_news = ArtsNewsFactory()
        NewsSlideshowImageFactory(news=slideshow_news)
        job_news = ArtsNewsFactory(is_job_opportunity=True)

        request = HttpRequest()
        view = NewsListView(request=request)
        news = view.get_queryset()
        self.assertIn(external_news, news)
        self.assertIn(video_news, news)
        self.assertIn(slideshow_news, news)
        self.assertIn(job_news, news)

        request.GET = {'category': 'external'}
        news = view.get_queryset()
        self.assertIn(external_news, news)
        self.assertNotIn(video_news, news)
        self.assertNotIn(slideshow_news, news)
        self.assertNotIn(job_news, news)

        request.GET = {'category': 'videos'}
        news = view.get_queryset()
        self.assertNotIn(external_news, news)
        self.assertIn(video_news, news)
        self.assertNotIn(slideshow_news, news)
        self.assertNotIn(job_news, news)

        request.GET = {'category': 'slideshows'}
        news = view.get_queryset()
        self.assertNotIn(external_news, news)
        self.assertNotIn(video_news, news)
        self.assertIn(slideshow_news, news)
        self.assertNotIn(job_news, news)

        request.GET = {'category': 'opportunities'}
        news = view.get_queryset()
        self.assertNotIn(external_news, news)
        self.assertNotIn(video_news, news)
        self.assertNotIn(slideshow_news, news)
        self.assertIn(job_news, news)

    def test_get_context_data(self):
        news = ArtsNewsFactory()
        request = HttpRequest()
        view = NewsListView(request=request)
        view.object_list = [news]

        request.GET = {'page': 2}
        with patch.object(Paginator, 'page', return_value='page') as mock_page:
            with patch.object(view, 'get_queryset', return_value=[news]):
                context = view.get_context_data()
        self.assertEqual(context['page'], 'page')
        mock_page.assert_called_once_with(2)

        with patch.object(
            Paginator,
            'page',
            side_effect=PageNotAnInteger()
        ) as mock_page:
            with patch.object(view, 'get_queryset', return_value=[news]):
                try:
                    context = view.get_context_data()
                except PageNotAnInteger:
                    pass
        mock_page.has_call(1)

        with patch.object(Paginator, 'page', side_effect=EmptyPage()) as mock:
            with patch.object(view, 'get_queryset', return_value=[news]):
                try:
                    context = view.get_context_data()
                except EmptyPage:
                    pass
        mock.has_call(1)


class ProductionNewsListViewTestCase(TestCase):
    def setUp(self):
        self.production = ProductionFactory()

    def test_inherits_base_class(self):
        self.assertIsInstance(ProductionNewsListView(), NewsListView)

    def test_class_attributes(self):
        self.assertEqual(
            ProductionNewsListView.template_name,
            'news/production.html'
        )

    def test_dispatch(self):
        request = HttpRequest()
        view = ProductionNewsListView(request=request)
        with patch.object(NewsListView, 'dispatch'):
            view.dispatch(request, slug=self.production.slug)
        self.assertEqual(view.production, self.production)

    def test_get_queryset(self):
        view = ProductionNewsListView()
        view.production = self.production
        queryset = ArtsNews.objects.all()
        with patch(
            'base.views.NewsListView.get_queryset',
            return_value=queryset
        ) as mock_get_query:
            all_news = view.get_queryset()
        mock_get_query.assert_called_once_with()
        self.assertEqual(
            len(all_news),
            len(queryset.filter(related_production=self.production))
        )

    def test_get_context_data(self):
        view = ProductionNewsListView()
        view.production = self.production
        with patch.object(NewsListView, 'get_context_data', return_value={}):
            context = view.get_context_data()
        self.assertEqual(context['production'], self.production)


class ProductionDetailViewTestCase(TestCase):
    def test_inherits_base_class(self):
        self.assertIsInstance(ProductionDetailView(), DetailView)

    def test_class_attributes(self):
        self.assertEqual(ProductionDetailView.model, Production)
        self.assertEqual(
            ProductionDetailView.template_name,
            'productions/detail.html'
        )

    def test_get_context_data(self):
        production = ProductionFactory()
        other_production = ProductionFactory()
        news = ArtsNewsFactory()

        view = ProductionDetailView()
        view.object = production
        with patch.object(
            ProductionDetailView,
            'get_object',
            return_value=production
        ):
            context = view.get_context_data()
        self.assertIn(other_production, context['current_productions'])
        self.assertNotIn(production, context['current_productions'])
        self.assertEqual(context['company_productions'], [])
        self.assertIn(news, context['recent_news'])

        company = ProductionCompanyFactory()
        company_production = ProductionFactory(production_company=company)
        production.production_company = company
        with patch.object(
            ProductionDetailView,
            'get_object',
            return_value=production
        ):
            context = view.get_context_data()
        self.assertIn(company_production, context['company_productions'])


class DateRangePerformanceViewTestCase(TestCase):
    def setUp(self):
        self.view = DateRangePerformanceView()

    def test_inherits_base_class(self):
        self.assertIsInstance(self.view, TemplateView)

    def test_class_attributes(self):
        self.assertEqual(DateRangePerformanceView.date_format, '%Y%m%d')
        self.assertEqual(DateRangePerformanceView.days_in_range, 0)

    def test_get_days_in_range(self):
        self.assertEqual(
            self.view._get_days_in_range(),
            DateRangePerformanceView.days_in_range
        )

    def test_get_start_date(self):
        self.view.kwargs = {}
        self.assertEqual(self.view._get_start_date(), date.today())
        self.view.kwargs = {'start_date': '20160804'}
        self.assertEqual(self.view._get_start_date(), date(2016, 8, 4))

    def test_get_range(self):
        start = date(2016, 8, 4)
        with patch.object(self.view, '_get_start_date', return_value=start):
            with patch.object(self.view, '_get_days_in_range', return_value=5):
                date_range = self.view._get_range()
        self.assertEqual(date_range, (start, start + timedelta(days=5)))

    def test_get_performances(self):
        start = timezone.now() - timedelta(days=5)
        end = timezone.now() - timedelta(days=2)
        production_1 = ProductionFactory(
            start_date=start + timedelta(days=1)
        )
        production_2 = ProductionFactory(
            start_date=start + timedelta(days=2)
        )

        with patch.object(self.view, '_get_range', return_value=(start, end)):
            performances = self.view.get_performances()
        self.assertEqual(performances[0], production_1)
        self.assertEqual(performances[1], production_2)

    def test_get_context_data(self):
        start = timezone.now() - timedelta(days=5)
        end = timezone.now() - timedelta(days=2)
        production = ProductionFactory()
        with patch.object(self.view, '_get_range', return_value=(start, end)):
            with patch.object(
                self.view,
                'get_performances',
                return_value=[production]
            ):
                context = self.view.get_context_data()
        self.assertEqual([production], context['productions'])
        self.assertEqual(start, context['start_date'])
        self.assertEqual(end, context['end_date'])


class UpcomingPerformanceViewTestCase(TestCase):
    def test_inherits_base_class(self):
        self.assertIsInstance(
            UpcomingPerformanceView(),
            DateRangePerformanceView
        )

    def test_class_attributes(self):
        self.assertEqual(UpcomingPerformanceView.days_in_range, 60)
        self.assertEqual(
            UpcomingPerformanceView.template_name,
            'productions/upcoming.html'
        )


class WeekPerformanceViewTestCase(TestCase):
    def test_inherits_base_class(self):
        self.assertIsInstance(WeekPerformanceView(), DateRangePerformanceView)

    def test_class_attributes(self):
        self.assertEqual(WeekPerformanceView.days_in_range, 7)
        self.assertEqual(
            WeekPerformanceView.template_name,
            'productions/weekly.html'
        )

    def test_get_context_data(self):
        start = timezone.now()
        end = start + timedelta(days=7)
        view = WeekPerformanceView()
        with patch.object(view, '_get_range', return_value=(start, end)):
            context = view.get_context_data()
        self.assertEqual(context['current_start_date'], start)
        self.assertEqual(context['next_start_date'], end + timedelta(days=1))
        self.assertEqual(context['next_end_date'], end + timedelta(days=7))
        self.assertEqual(
            context['previous_start_date'],
            start - timedelta(days=7)
        )
        self.assertEqual(
            context['previous_end_date'],
            start - timedelta(days=1)
        )


class MonthPerformanceViewTestCase(TestCase):
    def test_inherits_base_class(self):
        self.assertIsInstance(MonthPerformanceView(), DateRangePerformanceView)

    def test_class_attributes(self):
        self.assertEqual(
            MonthPerformanceView.template_name,
            'productions/monthly.html'
        )

    def test_get_start_date(self):
        view = MonthPerformanceView(kwargs={'month': '8', 'year': '2016'})
        self.assertEqual(view._get_start_date(), date(2016, 8, 1))

        view = MonthPerformanceView(kwargs={'month': '13', 'year': '2016'})
        self.assertEqual(view._get_start_date(), date(2016, 12, 1))

        view = MonthPerformanceView(kwargs={'month': '-1', 'year': '2016'})
        self.assertEqual(view._get_start_date(), date(2016, 1, 1))

        today = date.today()
        view = MonthPerformanceView(kwargs={})
        self.assertEqual(
            view._get_start_date(),
            date(today.year, today.month, 1),
        )

    def test_get_range(self):
        view = MonthPerformanceView()
        start_date = date(2016, 8, 4)
        with patch.object(view, '_get_start_date', return_value=start_date):
            date_range = view._get_range()
        self.assertEqual(date_range, (start_date, date(2016, 8, 31)))

    def test_get_context_data(self):
        view = MonthPerformanceView()
        start = timezone.now()
        end = start + timedelta(days=5)
        with patch.object(view, '_get_range', return_value=(start, end)):
            context = view.get_context_data()
        self.assertEqual(context['current_start_date'], start)
        self.assertEqual(context['next_start_date'], end + timedelta(days=1))
        self.assertEqual(
            context['previous_start_date'],
            start - timedelta(days=1)
        )


class CityPerformanceViewTestCase(TestCase):
    def test_inherits_base_class(self):
        self.assertIsInstance(CityPerformanceView(), ListView)

    def test_class_attributes(self):
        self.assertEqual(CityPerformanceView.model, Production)
        self.assertEqual(
            CityPerformanceView.template_name,
            'productions/city.html'
        )
        self.assertEqual(
            CityPerformanceView.context_object_name,
            'productions'
        )

    def test_dispatch(self):
        view = CityPerformanceView()
        request = HttpRequest()
        with patch('django.views.generic.list.ListView.dispatch') as mock:
            view.dispatch(request, city='Austin')
        self.assertEqual(view.city, 'Austin')
        mock.assert_called_once_with(request, city='Austin')

    def test_get_queryset(self):
        view = CityPerformanceView()
        view.city = None
        self.assertEqual(view.get_queryset(), [])

        view.city = 'Austin'
        production = ProductionFactory(
            venue=VenueFactory(address=AddressFactory(city='Austin'))
        )
        self.assertEqual(view.get_queryset()[0], production)

    def test_get_context_data(self):
        view = CityPerformanceView()
        view.city = 'Austin'
        austin_venue = VenueFactory(address=AddressFactory(city='Austin'))
        bastrop_venue = VenueFactory(address=AddressFactory(city='Bastrop'))
        ProductionFactory(venue=austin_venue)
        city_venues = {
            'Austin': [austin_venue],
            'Bastrop': [bastrop_venue],
        }
        with patch(
            'django.views.generic.list.ListView.get_context_data',
            return_value={}
        ):
            with patch.object(
                Venue.objects,
                'filter_cities',
                return_value=city_venues
            ):
                context = view.get_context_data()
        self.assertEqual(context['city'], 'Austin')
        self.assertIn('Austin', context['cities'])
        self.assertNotIn('Bastrop', context['cities'])


class CompanyObjectListViewTestCase(TestCase):
    def setUp(self):
        self.view = CompanyObjectListView()
        self.company = ProductionCompanyFactory()

    def test_inherits_base_class(self):
        self.assertIsInstance(self.view, ListView)

    def test_class_attributes(self):
        self.assertIsNone(CompanyObjectListView.model)
        self.assertIsNone(CompanyObjectListView.order_by)

    def test_dispatch(self):
        request = HttpRequest()
        with patch('django.views.generic.list.ListView.dispatch') as mock:
            self.view.dispatch(request, slug=self.company.slug)
        self.assertEqual(self.view.company, self.company)
        mock.assert_called_once_with(request, slug=self.company.slug)

    def test_get_queryset(self):
        self.view.model = Production
        self.view.company = self.company
        company_production = ProductionFactory(production_company=self.company)
        ProductionFactory()
        with patch.object(self.view, 'order_queryset') as mock_order_queryset:
            self.view.get_queryset()
        self.assertEqual(mock_order_queryset.call_count, 1)
        called_queryset = mock_order_queryset.call_args[0][0]
        self.assertEqual(called_queryset[0], company_production)

    def test_order_queryset(self):
        queryset = Production.objects.all()
        with patch.object(queryset, 'order_by') as mock_order_by:
            self.view.order_queryset(queryset)
        mock_order_by.assert_not_called()

        self.view.order_by = '-start_date'
        with patch.object(queryset, 'order_by') as mock_order_by:
            self.view.order_queryset(queryset)
        mock_order_by.assert_called_once_with('-start_date')

    def test_get_context_data(self):
        self.view.company = ProductionFactory()
        with patch(
            'django.views.generic.list.ListView.get_context_data',
            return_value={}
        ):
            context = self.view.get_context_data()
        self.assertEqual(context['company'], self.view.company)


class CompanyNewsListViewTestCase(TestCase):
    def test_inherits_base_classes(self):
        view = CompanyNewsListView()
        self.assertIsInstance(view, NewsListView)
        self.assertIsInstance(view, CompanyObjectListView)

    def test_class_attributes(self):
        self.assertEqual(CompanyNewsListView.order_by, '-created_on')
        self.assertEqual(
            CompanyNewsListView.template_name,
            'news/company.html'
        )

    def test_get_queryset(self):
        company = ProductionCompanyFactory()
        company_production = ProductionFactory(production_company=company)
        company_news = ArtsNewsFactory(related_company=company)
        production_news = ArtsNewsFactory(
            related_production=company_production
        )
        company_and_production_news = ArtsNewsFactory(
            related_company=company,
            related_production=company_production,
        )
        other_news = ArtsNewsFactory()

        view = CompanyNewsListView()
        view.company = company
        with patch.object(
            NewsListView,
            'get_queryset',
            return_value=ArtsNews.objects.all()
        ):
            queryset = view.get_queryset()
        self.assertIn(company_news, queryset)
        self.assertIn(production_news, queryset)
        self.assertIn(company_and_production_news, queryset)
        self.assertNotIn(other_news, queryset)
        self.assertEqual(len(queryset), 3)


class CompanyProductionListViewTestCase(TestCase):
    def test_inherits_base_class(self):
        self.assertIsInstance(
            CompanyProductionListView(),
            CompanyObjectListView
        )

    def test_class_attributes(self):
        self.assertEqual(CompanyProductionListView.model, Production)
        self.assertEqual(CompanyProductionListView.order_by, '-start_date')
        self.assertEqual(
            CompanyProductionListView.template_name,
            'productions/company.html'
        )
        self.assertEqual(
            CompanyProductionListView.context_object_name,
            'productions'
        )


class CompanyReviewListViewTestCase(TestCase):
    def test_inherits_base_classes(self):
        view = CompanyReviewListView()
        self.assertIsInstance(view, CompanyObjectListView)
        self.assertIsInstance(view, ReviewListView)

    def test_class_attributes(self):
        self.assertEqual(CompanyReviewListView.model, Review)
        self.assertEqual(CompanyReviewListView.order_by, '-published_on')
        self.assertEqual(
            CompanyReviewListView.template_name,
            'reviews/company.html'
        )

    def test_get_queryset(self):
        company = ProductionCompanyFactory()
        production = ProductionFactory(production_company=company)
        published_review = ReviewFactory(
            is_published=True,
            production=production,
        )
        unpublished_review = ReviewFactory(
            is_published=False,
            production=production,
        )
        other_review = ReviewFactory(is_published=True)

        view = CompanyReviewListView()
        view.company = company
        with patch.object(
            view,
            'order_queryset',
            return_value='foobar'
        ) as mock_order_queryset:
            queryset = view.get_queryset()
        self.assertEqual(queryset, 'foobar')
        self.assertEqual(mock_order_queryset.call_count, 1)
        mocked_queryset = mock_order_queryset.call_args[0][0]
        self.assertIn(published_review, mocked_queryset)
        self.assertNotIn(unpublished_review, mocked_queryset)
        self.assertNotIn(other_review, mocked_queryset)


class CompanyAuditionListViewTestCase(TestCase):
    def test_inherits_base_classes(self):
        view = CompanyAuditionListView()
        self.assertIsInstance(view, UpcomingAuditionListView)
        self.assertIsInstance(view, CompanyObjectListView)

    def test_class_attributes(self):
        self.assertEqual(CompanyAuditionListView.model, Audition)
        self.assertEqual(CompanyAuditionListView.order_by, 'start_date')
        self.assertEqual(
            CompanyAuditionListView.template_name,
            'auditions/company_upcoming.html'
        )

    def test_get_queryset(self):
        company = ProductionCompanyFactory()
        audition_1 = AuditionFactory(
            production_company=company,
            start_date=timezone.now() + timedelta(days=1)
        )
        audition_2 = AuditionFactory(
            production_company=company,
            start_date=timezone.now() + timedelta(days=2)
        )

        view = CompanyAuditionListView()
        view.company = company
        queryset = view.get_queryset()
        self.assertEqual(queryset[0], audition_1)
        self.assertEqual(queryset[1], audition_2)


class CompanyPastAuditionListViewTestCase(TestCase):
    def test_inherit_base_classes(self):
        view = CompanyPastAuditionListView()
        self.assertIsInstance(view, PastAuditionListView)
        self.assertIsInstance(view, CompanyObjectListView)

    def test_class_attributes(self):
        self.assertEqual(CompanyPastAuditionListView.model, Audition)
        self.assertEqual(CompanyPastAuditionListView.order_by, 'start_date')
        self.assertEqual(
            CompanyPastAuditionListView.template_name,
            'auditions/company_past.html'
        )

    def test_get_queryset(self):
        company = ProductionCompanyFactory()
        company_audition = AuditionFactory(production_company=company)
        other_audition = AuditionFactory()

        view = CompanyPastAuditionListView()
        view.company = company
        with patch.object(
            PastAuditionListView,
            'get_queryset',
            return_value=Audition.objects.all()
        ):
            queryset = view.get_queryset()
        self.assertIn(company_audition, queryset)
        self.assertNotIn(other_audition, queryset)


class VenueListViewTestCase(TestCase):
    def test_inherit_base_class(self):
        self.assertIsInstance(VenueListView(), ListView)

    def test_class_attributes(self):
        self.assertEqual(VenueListView.model, Venue)
        self.assertEqual(VenueListView.template_name, 'venues/list.html')

    def test_get_queryset(self):
        austin_venue = VenueFactory(address=AddressFactory(city='Austin'))
        bastrop_venue = VenueFactory(address=AddressFactory(city='Bastrop'))
        ProductionFactory(venue=austin_venue)
        ProductionFactory(venue=bastrop_venue)

        view = VenueListView()
        queryset = view.get_queryset()
        self.assertEqual(queryset[0][0], u'Austin')
        self.assertEqual(queryset[0][1][0], austin_venue)
        self.assertEqual(queryset[1][0], u'Bastrop')
        self.assertEqual(queryset[1][1][0], bastrop_venue)


class VenueProductionListViewTestCase(TestCase):
    def setUp(self):
        self.venue = VenueFactory()

    def test_inherits_base_class(self):
        self.assertIsInstance(VenueProductionListView(), ListView)

    def test_class_attributes(self):
        self.assertEqual(VenueProductionListView.model, Production)
        self.assertEqual(
            VenueProductionListView.template_name,
            'productions/venue.html'
        )
        self.assertEqual(
            VenueProductionListView.context_object_name,
            'productions'
        )

    def test_dispatch(self):
        view = VenueProductionListView()
        request = HttpRequest()
        with patch('django.views.generic.list.ListView.dispatch'):
            view.dispatch(request, slug=self.venue.slug)
        self.assertEqual(view.venue, self.venue)

    def test_get_queryset(self):
        venue_production_1 = ProductionFactory(
            venue=self.venue,
            start_date=timezone.now() - timedelta(days=1)
        )
        venue_production_2 = ProductionFactory(
            venue=self.venue,
            start_date=timezone.now() - timedelta(days=2)
        )
        other_production = ProductionFactory()

        view = VenueProductionListView()
        view.venue = self.venue
        queryset = view.get_queryset()
        self.assertNotIn(other_production, queryset)
        self.assertEqual(queryset[0], venue_production_1)
        self.assertEqual(queryset[1], venue_production_2)

    def test_get_context_data(self):
        view = VenueProductionListView()
        view.venue = self.venue
        with patch(
            'django.views.generic.list.ListView.get_context_data',
            return_value={}
        ):
            context = view.get_context_data(self)
        self.assertEqual(context['venue'], self.venue)


class ReviewerListViewTestCase(TestCase):
    def test_inherits_base_class(self):
        self.assertIsInstance(ReviewerListView(), ListView)

    def test_class_attributes(self):
        self.assertEqual(ReviewerListView.model, Reviewer)
        self.assertEqual(
            ReviewerListView.template_name,
            'about/reviewers.html'
        )

    def test_get_context_data(self):
        reviewer_1 = ReviewerFactory()
        ReviewFactory(reviewer=reviewer_1, published_on=timezone.now())
        ReviewFactory(reviewer=reviewer_1, published_on=timezone.now())
        reviewer_2 = ReviewerFactory()
        ReviewFactory(reviewer=reviewer_2, published_on=timezone.now())
        inactive_reviewer = ReviewerFactory()

        view = ReviewerListView()
        with patch(
            'django.views.generic.list.ListView.get_context_data',
            return_value={}
        ):
            context = view.get_context_data()
        self.assertIn(reviewer_1, context['active_reviewers'])
        self.assertIn(reviewer_2, context['active_reviewers'])
        self.assertEqual(context['inactive_reviewers'][0], inactive_reviewer)


class AboutViewTestCase(TestCase):
    def test_inherits_base_class(self):
        self.assertIsInstance(AboutView(), TemplateView)

    def test_class_attributes(self):
        self.assertEqual(AboutView.template_name, 'about/base.html')


class PrinciplesServicesViewTestCase(TestCase):
    def test_inherits_base_class(self):
        self.assertIsInstance(PrinciplesServicesView(), TemplateView)

    def test_class_attirbutes(self):
        self.assertEqual(
            PrinciplesServicesView.template_name,
            'about/principles_and_services.html'
        )


class ContactFormViewTestCase(TestCase):
    def test_inherits_base_class(self):
        self.assertIsInstance(ContactFormView(), FormView)

    def test_class_attributes(self):
        self.assertEqual(ContactFormView.form_class, ContactForm)
        self.assertEqual(ContactFormView.template_name, 'about/contact.html')

    def test_get_success_url(self):
        self.assertIsInstance(ContactFormView().get_success_url(), str)

    def test_form_valid(self):
        view = ContactFormView()
        form = ContactForm()
        with patch.object(form, 'send_message') as mock_send_message:
            with patch.object(FormView, 'form_valid', return_value='foobar'):
                result = view.form_valid(form)
        mock_send_message.assert_called_once_with()
        self.assertEqual(result, 'foobar')


class ContactThanksViewTestCase(TestCase):
    def test_inherits_base_class(self):
        self.assertIsInstance(ContactThanksView(), TemplateView)

    def test_class_attributes(self):
        self.assertEqual(
            ContactThanksView.template_name,
            'about/contact_thanks.html'
        )
