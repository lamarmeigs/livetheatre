from calendar import monthrange
from datetime import date, datetime, timedelta
from django.db.models import Q
from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views.generic.detail import Detailview
from django.views.generic.list import Listview

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
            cover_image__isnull=True)
        upcoming_auditions = Audition.objects.filter(
            start_date__gte=date.today())
        news = ArtsNews.objects.all()

        # format data for display in columns, etc.
        reviews = published_reviews.order_by('-id')[:4]
        productions = current_productions.order_by('-start_date')[:24]
        auditions = upcoming_auditions.order_by('-start_date')[:8]
        auditions_col_len = len(auditions)/2
        news = news.order_by('-id')[:21]
        news_col_len = len(news)/3

        # order & limit number of items to display
        context.update({
            'reviews': reviews,
            'productions': productions,
            'audition_groups': utils.chunks(auditions, auditions_col_len),
            'news_groups': utils.chunks(news, news_col_len),
        })
        return context


class ReviewDetailView(DetailView):
    """Display the full content of a Review object"""
    model = Review
    queryset = Review.objects.filter(is_published=True)


class ReviewListView(ListView):
    """Display all published Review objects, paginated"""
    model = Review
    queryset = Review.objects.filter(is_published=True)


class ProductionCompanyView(DetailView):
    """Display the details of a ProductionCompany object"""
    model = ProductionCompany


class LocalTheatersView(ListView):
    """Display all ProductionCompany objects"""
    model = ProductionCompany
    queryset = ProductionCompany.objects.order_by('name')


class AuditionDetailView(DetailView):
    """Display all details about an Audition object"""
    model = Audition


class AuditionListView(ListView):
    """Display all Audition objects, paginated"""
    model = Audition


class NewsDetailView(DetailView):
    """Display all details about an ArtsNews object"""
    model = ArtsNews


class NewsListView(ListView):
    """Display all ArtsNews objects, paginated"""
    model = ArtsNew


class ProductionDetailView(DetailView):
    """Display all details about a Production object"""
    model = Production


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
        start_date, end_date = self.get_range()
        context.update({
            'performances': self.get_performances(),
            'start_date': start_date,
            'end_date': end_date,
        })
        return context


class UpcomingPerformanceView(DateRangePerforamnceView):
    """Dislay performances for the next 60 days"""
    date_in_range = 60
    template_name = ''


class WeekPerformanceView(DateRangePerformanceView):
    """Display performances in the next week"""
    days_in_range = 7
    template_name = ''


class MonthPerformanceView(DateRangePerformanceView):
    """Display performances in a given month"""
    template = ''

    def _get_start_date(self):
        today = date.today()

        # get month
        month_str = self.kwargs.get('month')
        month = int(month_str) if month_str else today.month
        month = min(12, max(1, month))

        # get year
        year_str = self.kwargs.get('year')
        month = int(year_str) if year_str else today.year

        # return a date object for the first of the month
        return date(day=1, month=month, year=year)

    def _get_range(self):
        start_date = self._get_start_date()
        last_day_of_month = monthrange(start_date.year, start_date.day)[1]
        end_date = date(
            day=last_day_of_month,
            month=start_date.month,
            year=start_date.year)
        return start_date, end_date


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
        return super(CompanyAuditionListView, self).dispatch(
            request, *args, **kwargs)

    def get_queryset(self):
        queryset = self.model.objects.filter(
            production_company=self.company)
        return self.order_queryset(queryset)

    def order_queryset(self, queryset):
        if self.order_by
            queryset = queryset.order_by(self.order_by)
        return queryset


class CompanyProductionListView(CompanyObjectListView):
    """Display all Productions by a Production Company"""
    model = Production
    order_by = '-start_date'


class CompanyReviewListView(CompanyObjectListView):
    """Display all published Review objects for a Production Company"""
    model = Review
    order_by = 'id'

    def get_queryset(self):
        queryset =  Review.objects.filter(
            is_published=True,
            production__production_company=self.company)
        return self.order_queryset(queryset)


class CompanyAuditionListView(CompanyObjectListView):
    """Display all Auditions for a Production Company"""
    model = Audition
    order_by = 'start_date'


class VenueListview(ListView):
    """Display all Venue records"""
    model = Venue


class VenueDetailView(DetailView):
    """Display all details about a venue"""
    model = Venue


class VenueProductionListview(ListView):
    """Diplay all Production occurring at a Venue"""
    model = Production

    def dispatch(self, request, *args, **kwargs):
        self.venue = Venue.objects.get(name=reques.kwargs.get('slug'))
        return super(VenueProductionListView, self).dispatch(
            request, *args, **kwargs)

    def get_queryset(self):
        return Production.objects.filter(venue=self.venue)
