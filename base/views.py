from calendar import monthrange
from datetime import date, datetime, timedelta
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from base import utils
from base.models import *


class HomepageView(TemplateView):
    """The site's homepage"""
    template_name = 'homepage.html'

    def get_context_data(self, *args, **kwargs):
        context = super(HomepageView, self).get_context_data(*args, **kwargs)

        # get reviews, productions, auditions, and news to display
        today = date.today()
        published_reviews = Review.objects.filter(is_published=True)
        current_productions = Production.objects.filter_current().exclude(
            poster__isnull=True)
        upcoming_auditions = Audition.objects.filter(
            start_date__gte=date.today())
        news = ArtsNews.objects.all()

        # limit records displayed on page
        reviews = published_reviews.order_by('-id')[:4]
        productions = current_productions.order_by('-start_date')[:24]

        # format data for display in columns, etc.
        auditions = upcoming_auditions.order_by('-start_date')[:8]
        auditions_col_len = len(auditions)/2
        audition_groups = utils.chunks(auditions, auditions_col_len) \
            if auditions_col_len else [list(auditions)]
            
        news = news.order_by('-created_on')[:21]
        news_col_len = len(news)/3
        news_groups = utils.chunks(news, news_col_len) \
            if news_col_len else [list(news)]

        # order & limit number of items to display
        context.update({
            'reviews': reviews,
            'productions': productions,
            'audition_groups': audition_groups,
            'news_groups': news_groups,
        })
        return context


class ReviewDetailView(DetailView):
    """Display the full content of a Review object"""
    model = Review
    queryset = Review.objects.filter(is_published=True)
    template_name = 'reviews/detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ReviewDetailView, self).get_context_data(
            *args, **kwargs)

        recent_reviews = Review.objects.all()
        recent_news = ArtsNews.objects.all()

        review = self.get_object()
        company = review.production.production_company
        company_productions = \
            company.production_set.exclude(pk=review.production.pk) \
            if company else []

        context.update({
            'recent_reviews': recent_reviews[:5],
            'company_productions': company_productions[:5],
            'recent_news': recent_news[:5],
        })
        return context


class ReviewListView(ListView):
    """Display all published Review objects, paginated"""
    model = Review
    queryset = Review.objects.filter(is_published=True)
    template_name = 'reviews/list.html'


class ProductionCompanyView(DetailView):
    """Display the details of a ProductionCompany object"""
    model = ProductionCompany
    template_name = 'companies/detail.html'


class LocalTheatresView(ListView):
    """Display all ProductionCompany objects"""
    model = ProductionCompany
    queryset = ProductionCompany.objects.order_by('name')
    template_name = 'companies/list.html'


class AuditionDetailView(DetailView):
    """Display all details about an Audition object"""
    model = Audition
    template_name = 'auditions/detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super(AuditionDetailView, self).get_context_data(
            *args, **kwargs)

        upcoming_auditions = Audition.objects.filter_upcoming()
        recent_news = ArtsNews.objects.all()

        audition = self.get_object()
        company = audition.production_company
        company_productions = company.production_set.all() \
            if company else []

        context.update({
            'upcoming_auditions': upcoming_auditions[:3],
            'company_productions': company_productions[:3],
            'recent_news': recent_news[:3],
        })
        return context


class AuditionListView(ListView):
    """Display all Audition objects, paginated"""
    model = Audition
    template_name = 'auditions/list.html'

    def get_context_data(self, *args, **kwargs):
        context = super(AuditionListView, self).get_context_data(
            *args, **kwargs)

        # split upcoming and past auditions
        upcoming = Audition.objects.filter_upcoming()
        all_past = Audition.objects.exclude(
            id__in=[audition.id for audition in upcoming]
            ).order_by('-start_date')

        # paginate past auditions
        paginator = Paginator(all_past, 30)
        page = self.request.GET.get('page')
        try:
            page = paginator.page(page)
        except PageNotAnInteger:
            page = paginator.page(1)
        except EmptyPage:
            page = paginator.page(paginator.num_pages)

        # break past auditions into column groupings
        past_auditions = page.object_list
        column_length = len(past_auditions)/2
        past_audition_groups = utils.chunks(past_auditions, column_length) \
            if column_length else [list(past_auditions)]

        context.update({
            'upcoming_auditions': upcoming,
            'past_audition_groups': past_audition_groups,
            'page': page,
        })
        return context


class NewsDetailView(DetailView):
    """Display all details about an ArtsNews object"""
    model = ArtsNews
    template_name = 'news/detail.html'
    context_object_name = 'news'

    def get_context_data(self, *args, **kwargs):
        context = super(NewsDetailView, self).get_context_data(
            *args, **kwargs)

        news = self.get_object()
        recent_reviews = Review.objects.all()
        recent_news = ArtsNews.objects.exclude(pk=news.pk)
        current_productions = Production.objects.filter_current()

        context.update({
            'recent_reviews': recent_reviews[:3],
            'recent_news': recent_news[:3],
            'current_productions': current_productions[:3],
        })

        return context


class NewsListView(ListView):
    """Display all ArtsNews objects, paginated"""
    model = ArtsNews
    template_name = 'news/list.html'


class ProductionDetailView(DetailView):
    """Display all details about a Production object"""
    model = Production
    template_name = 'productions/detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ProductionDetailView, self).get_context_data(
            *args, **kwargs)

        production = self.get_object()
        current_productions = Production.objects.filter_current().exclude(
            pk=production.pk)
        recent_news = ArtsNews.objects.all()

        production = self.get_object()
        company = production.production_company
        if company:
            company_productions = company.production_set.exclude(
                pk=production.pk)
        else:
            company_productions = []

        context.update({
            'current_productions': current_productions[:3],
            'company_productions': company_productions[:3],
            'recent_news': recent_news[:3],
        })
        return context


class DateRangePerformanceView(TemplateView):
    """
    Base view returning Productions occurring during specified date range
    
    date_format - strptime format to use when reading url parameters
    days_in_range - integer to define the duration of the date range
    """
    date_format = '%Y%m%d'
    days_in_range = 0

    def _get_days_in_range(self):
        """Return the number of days in the range to search"""
        return self.days_in_range

    def _get_start_date(self):
        """
        Return the first date in the range to search. If no start_date
        parameter is provided in the url, return the current day.
        """
        start_date_str = self.kwargs.get('start_date')
        if start_date_str:
            start_datetime = datetime.strptime(
                start_date_str, self.date_format)
            start_date = start_datetime.date()
        else:
            start_date = date.today()
        return start_date

    def _get_range(self):
        """Return the start_date and end_date of the date range (inclusive)"""
        start_date = self._get_start_date()
        return start_date, start_date + timedelta(days=self._get_days_in_range())

    def get_performances(self):
        """Return all Production objects in the specified date range"""
        start_date, end_date = self._get_range()
        return Production.objects.filter_in_range(start_date, end_date)

    def get_context_data(self, *args, **kwargs):
        context = super(DateRangePerformanceView, self).get_context_data(
            *args, **kwargs)
        start_date, end_date = self._get_range()
        context.update({
            'productions': self.get_performances(),
            'start_date': start_date,
            'end_date': end_date,
        })
        return context


class UpcomingPerformanceView(DateRangePerformanceView):
    """Dislay performances for the next 60 days"""
    date_in_range = 60
    template_name = 'productions/upcoming.html'


class WeekPerformanceView(DateRangePerformanceView):
    """Display performances in the next week"""
    days_in_range = 7
    template_name = 'productions/weekly.html'

    def get_context_data(self, *args, **kwargs):
        context = super(WeekPerformanceView, self).get_context_data(
            *args, **kwargs)

        start_date, end_date = self._get_range()

        next_start_date = end_date + timedelta(days=1)
        next_end_date = end_date + timedelta(days=7)

        previous_start_date = start_date - timedelta(days=7)
        previous_end_date = start_date - timedelta(days=1)

        context.update({
            'current_start_date': start_date,
            'next_start_date': next_start_date,
            'next_end_date': next_end_date,
            'previous_start_date': previous_start_date,
            'previous_end_date': previous_end_date,
        })
        return context


class MonthPerformanceView(DateRangePerformanceView):
    """Display performances in a given month"""
    template_name = 'productions/monthly.html'

    def _get_start_date(self):
        today = date.today()

        # get month
        month_str = self.kwargs.get('month')
        month = int(month_str) if month_str else today.month
        month = min(12, max(1, month))

        # get year
        year_str = self.kwargs.get('year')
        year = int(year_str) if year_str else today.year

        # return a date object for the first of the month
        return date(day=1, month=month, year=year)

    def _get_range(self):
        start_date = self._get_start_date()
        last_day_of_month = monthrange(start_date.year, start_date.month)[1]
        end_date = date(
            day=last_day_of_month,
            month=start_date.month,
            year=start_date.year)
        return start_date, end_date

    def get_context_data(self, *args, **kwargs):
        context = super(MonthPerformanceView, self).get_context_data(
            *args, **kwargs)

        start_date, end_date = self._get_range()
        next_start_date = end_date + timedelta(days=1)
        previous_start_date = start_date - timedelta(days=1)

        context.update({
            'current_start_date': start_date,
            'next_start_date': next_start_date,
            'previous_start_date': previous_start_date,
        })
        return context


class CompanyObjectListView(ListView):
    """
    Base view to retrieve objects connected to a Production Company

    model - The model class whose objects to return
    order_by - an optional string defining the order to apply to the queryset
    """
    model = None
    order_by = None

    def dispatch(self, request, *args, **kwargs):
        self.company = get_object_or_404(
            ProductionCompany, slug=request.kwargs.get('slug'))
        return super(CompanyObjectListView, self).dispatch(
            request, *args, **kwargs)

    def get_queryset(self):
        queryset = self.model.objects.filter(
            production_company=self.company)
        return self.order_queryset(queryset)

    def order_queryset(self, queryset):
        if self.order_by:
            queryset = queryset.order_by(self.order_by)
        return queryset


class CompanyProductionListView(CompanyObjectListView):
    """Display all Productions by a Production Company"""
    model = Production
    order_by = '-start_date'
    template_name = 'productions/company.html'


class CompanyReviewListView(CompanyObjectListView):
    """Display all published Review objects for a Production Company"""
    model = Review
    order_by = 'id'
    template_name = 'reviews/company.html'

    def get_queryset(self):
        queryset =  Review.objects.filter(
            is_published=True,
            production__production_company=self.company)
        return self.order_queryset(queryset)


class CompanyAuditionListView(CompanyObjectListView):
    """Display all Auditions for a Production Company"""
    model = Audition
    order_by = 'start_date'
    template_name = 'auditions/company.html'


class VenueListView(ListView):
    """Display all Venue records"""
    model = Venue
    template_name = 'venues/list.html'


class VenueDetailView(DetailView):
    """Display all details about a venue"""
    model = Venue
    template_name = 'venues/detail.html'


class VenueProductionListView(ListView):
    """Diplay all Production occurring at a Venue"""
    model = Production
    template_name = 'productions/venue.html'

    def dispatch(self, request, *args, **kwargs):
        self.venue = Venue.objects.get(name=reques.kwargs.get('slug'))
        return super(VenueProductionListView, self).dispatch(
            request, *args, **kwargs)

    def get_queryset(self):
        return Production.objects.filter(venue=self.venue)
