from calendar import monthrange
from datetime import date, datetime, timedelta
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView

from base import utils, forms
from base.models import (
    ArtsNews, Audition, Production, ProductionCompany, Review, Reviewer, Venue
)


class HomepageView(TemplateView):
    """The site's homepage"""
    template_name = 'homepage.html'

    def get_context_data(self, *args, **kwargs):
        context = super(HomepageView, self).get_context_data(*args, **kwargs)

        # get reviews, productions, auditions, and news to display
        published_reviews = Review.objects.filter(
            is_published=True,
            cover_image__isnull=False
        ).exclude(cover_image='')
        current_productions = Production.objects.filter_current().exclude(
            poster__isnull=True)
        upcoming_auditions = Audition.objects.filter(
            start_date__gte=date.today())
        media_news = ArtsNews.objects.filter_media()
        news = ArtsNews.objects.order_by('-created_on')

        # limit records displayed on page
        reviews = published_reviews[:4]
        productions = current_productions.order_by('start_date')[:24]

        # format data for display in columns, etc.
        auditions = upcoming_auditions.order_by('start_date')[:8]
        if auditions:
            auditions_col_len = int(len(auditions)/2)
            audition_groups = [
                list(group) for group in utils.chunks(auditions, auditions_col_len)
            ]
        else:
            audition_groups = None

        # extract the latest news item with feature media
        media_news = media_news[0] if media_news else None

        # get the proper number of non-media news items
        max_news_per_column = 4
        news_columns = 3
        news = news.exclude(pk=media_news.pk) if media_news else news
        if news:
            news = news[:news_columns * max_news_per_column]
            news_column_length = int(len(news)/news_columns)
            news_groups = [
                list(news_column) for news_column in utils.chunks(news, news_column_length)
            ]
            news_groups = news_groups[:news_columns]
        else:
            news_groups = None

        # order & limit number of items to display
        context.update({
            'reviews': reviews,
            'productions': productions,
            'audition_groups': audition_groups,
            'media_news': media_news,
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

        recent_reviews = Review.objects.filter(is_published=True)
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
    queryset = Review.objects.filter(is_published=True).order_by(
        '-published_on')
    template_name = 'reviews/list.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ReviewListView, self).get_context_data(*args, **kwargs)

        # paginate reviews
        all_reviews = self.get_queryset()
        paginator = Paginator(all_reviews, 6)
        page = self.request.GET.get('page')
        try:
            page = paginator.page(page)
        except PageNotAnInteger:
            page = paginator.page(1)
        except EmptyPage:
            page = paginator.page(paginator.num_pages)

        context.update({
            'reviews': page.object_list,
            'page': page,
        })
        return context


class ProductionCompanyView(DetailView):
    """Display the details of a ProductionCompany object"""
    model = ProductionCompany
    template_name = 'companies/detail.html'
    context_object_name = 'company'

    def get_context_data(self, *args, **kwargs):
        context = super(ProductionCompanyView, self).get_context_data(
            *args, **kwargs)
        context['related_news'] = self.object.get_related_news()
        return context


class LocalTheatresView(ListView):
    """Display all ProductionCompany objects"""
    model = ProductionCompany
    queryset = ProductionCompany.objects.filter_active()
    template_name = 'companies/list.html'
    context_object_name = 'companies'

    def get_queryset(self):
        active_companies = self.queryset

        # categorize companies by the first letter in their name
        categorized = {}
        for company in active_companies:
            first_letter = (
                company.name[len('the ')].upper()
                if company.name.lower().startswith('the ')
                else company.name[0].upper()
            )
            if first_letter in categorized.keys():
                categorized[first_letter].append(company)
            else:
                categorized[first_letter] = [company]

        # sort companies alphabetically into a list of tuples
        ordered = []
        ordered_categories = sorted(categorized.keys())
        for category in ordered_categories:
            ordered.append((category, categorized.get(category)))

        return ordered


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


class UpcomingAuditionListView(ListView):
    """Display all upcoming Audition objects"""
    model = Audition
    queryset = Audition.objects.filter_upcoming().order_by('start_date')
    template_name = 'auditions/upcoming_list.html'


class PastAuditionListView(ListView):
    """Display all past Audition objects, paginated"""
    model = Audition
    template_name = 'auditions/past_list.html'

    def get_queryset(self):
        upcoming = Audition.objects.filter_upcoming()
        return Audition.objects.exclude(
            id__in=[audition.id for audition in upcoming]
            ).order_by('-start_date')

    def get_context_data(self, *args, **kwargs):
        context = super(PastAuditionListView, self).get_context_data(
            *args, **kwargs)

        # paginate past auditions
        auditions = self.get_queryset()
        paginator = Paginator(auditions, 24)
        page = self.request.GET.get('page')
        try:
            page = paginator.page(page)
        except PageNotAnInteger:
            page = paginator.page(1)
        except EmptyPage:
            page = paginator.page(paginator.num_pages)

        context['page'] = page
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

    def get_queryset(self):
        # if a category is provided, return only news items in that category
        category = self.request.GET.get('category')
        if category == 'external':
            news = ArtsNews.objects.filter(external_url__isnull=False).exclude(
                external_url='')
        elif category == 'videos':
            news = ArtsNews.objects.filter(video_embed__isnull=False).exclude(
                video_embed='')
        elif category == 'slideshows':
            news = ArtsNews.objects.filter(
                newsslideshowimage__isnull=False).distinct()
        elif category == 'opportunities':
            news = ArtsNews.objects.filter(is_job_opportunity=True)
        else:
            news = ArtsNews.objects.all()

        return news

    def get_context_data(self, *args, **kwargs):
        context = super(NewsListView, self).get_context_data(*args, **kwargs)

        # paginate news
        news_stories = self.get_queryset()
        stories_per_page = 36
        paginator = Paginator(news_stories, stories_per_page)
        page = self.request.GET.get('page')
        try:
            page = paginator.page(page)
        except PageNotAnInteger:
            page = paginator.page(1)
        except EmptyPage:
            page = paginator.page(paginator.num_pages)

        context['page'] = page
        return context


class ProductionNewsListView(NewsListView):
    """Display all news items associated with a production"""
    template_name = 'news/production.html'

    def dispatch(self, request, *args, **kwargs):
        self.production = get_object_or_404(Production, slug=kwargs['slug'])
        return super(ProductionNewsListView, self).dispatch(
            request, *args, **kwargs)

    def get_queryset(self):
        all_news = super(ProductionNewsListView, self).get_queryset()
        return all_news.filter(related_production=self.production)

    def get_context_data(self, *args, **kwargs):
        context = super(ProductionNewsListView, self).get_context_data(
            *args, **kwargs)
        context['production'] = self.production
        return context


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
        productions = Production.objects.filter_in_range(start_date, end_date)
        return productions.order_by('start_date')

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
    days_in_range = 60
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


class CityPerformanceView(ListView):
    """List all Production in a specified city"""
    model = Production
    template_name = 'productions/city.html'
    context_object_name = 'productions'

    def dispatch(self, request, *args, **kwargs):
        self.city = kwargs.get('city')
        return super(CityPerformanceView, self).dispatch(
            request, *args, **kwargs)

    def get_queryset(self):
        now = timezone.now()
        sixty_days = now + timedelta(days=60)
        current_queryset = Production.objects.filter_in_range(now, sixty_days)
        queryset = (
            current_queryset.filter(
                venue__address__city=self.city
            ).order_by('start_date') if self.city else []
        )
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super(CityPerformanceView, self).get_context_data(
            *args, **kwargs)

        # add list of cities, sorted by number of venues
        city_venues = Venue.objects.filter_cities()
        sorted_city_venues = sorted(
            city_venues.items(),
            key=lambda c: len(c[1]),
            reverse=True)
        cities = [cv[0] for cv in sorted_city_venues]

        # remove any cities that do not have upcoming productions
        upcoming_cities = Production.objects.filter_current().values_list(
            'venue__address__city', flat=True).distinct()
        cities = [city for city in cities if city in upcoming_cities]

        context.update({
            'city': self.city,
            'cities': cities,
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
            ProductionCompany, slug=kwargs.get('slug'))
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

    def get_context_data(self, *args, **kwargs):
        context = super(CompanyObjectListView, self).get_context_data(
            *args, **kwargs)
        context['company'] = self.company
        return context


class CompanyNewsListView(NewsListView, CompanyObjectListView):
    """Display all ArtsNews related to a Production Company"""
    order_by = '-created_on'
    template_name = 'news/company.html'

    def get_queryset(self):
        all_news = super(CompanyNewsListView, self).get_queryset()
        return all_news.filter(
            Q(related_company=self.company) |
            Q(related_production__production_company=self.company)).distinct()


class CompanyProductionListView(CompanyObjectListView):
    """Display all Productions by a Production Company"""
    model = Production
    order_by = '-start_date'
    template_name = 'productions/company.html'
    context_object_name = 'productions'


class CompanyReviewListView(CompanyObjectListView, ReviewListView):
    """Display all published Review objects for a Production Company"""
    model = Review
    order_by = '-published_on'
    template_name = 'reviews/company.html'

    def get_queryset(self):
        queryset = Review.objects.filter(
            is_published=True,
            production__production_company=self.company)
        return self.order_queryset(queryset)


class CompanyAuditionListView(UpcomingAuditionListView, CompanyObjectListView):
    """Display all Auditions for a Production Company"""
    model = Audition
    order_by = 'start_date'
    template_name = 'auditions/company_upcoming.html'

    def get_queryset(self):
        upcoming = super(CompanyAuditionListView, self).queryset
        return upcoming.filter(production_company=self.company).order_by(
            'start_date')


class CompanyPastAuditionListView(PastAuditionListView, CompanyObjectListView):
    """Display all Auditions for a Production Company"""
    model = Audition
    order_by = 'start_date'
    template_name = 'auditions/company_past.html'

    def get_queryset(self):
        past = super(CompanyPastAuditionListView, self).get_queryset()
        return past.filter(production_company=self.company)


class VenueListView(ListView):
    """Display all Venue records, by city"""
    model = Venue
    template_name = 'venues/list.html'

    def get_queryset(self, *args, **kwargs):
        """Return a dictionary that categorizes active venues by city"""
        venues = Venue.objects.filter_active()
        cities = venues.values_list('address__city', flat=True).distinct()
        city_venues = {}
        for city in cities:
            city_venues[city] = venues.filter(address__city=city)
        return sorted(city_venues.items())


class VenueProductionListView(ListView):
    """Display all Production occurring at a Venue"""
    model = Production
    template_name = 'productions/venue.html'
    context_object_name = 'productions'

    def dispatch(self, request, *args, **kwargs):
        self.venue = get_object_or_404(Venue, slug=kwargs.get('slug'))
        return super(VenueProductionListView, self).dispatch(
            request, *args, **kwargs)

    def get_queryset(self):
        return Production.objects.filter(venue=self.venue).order_by(
            '-start_date')

    def get_context_data(self, *args, **kwargs):
        context = super(VenueProductionListView, self).get_context_data(
            *args, **kwargs)
        context['venue'] = self.venue
        return context


class ReviewerListView(ListView):
    """Display all Reviewers, ordered by activity"""
    model = Reviewer
    template_name = 'about/reviewers.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ReviewerListView, self).get_context_data(
            *args, **kwargs)

        # ensure reviewers are sorted by activity
        active_reviewers = Reviewer.objects.filter_active()
        active_reviewers = sorted(
            list(active_reviewers),
            key=lambda r: r.review_set.count(),
            reverse=True)

        context.update({
            'active_reviewers': active_reviewers,
            'inactive_reviewers': Reviewer.objects.filter_inactive(),
        })
        return context


class AboutView(TemplateView):
    """Render static About page"""
    template_name = 'about/base.html'


class PrinciplesServicesView(TemplateView):
    """Render static Principles & Services page"""
    template_name = 'about/principles_and_services.html'


class ContactFormView(FormView):
    """Handles the contact form"""
    form_class = forms.ContactForm
    template_name = 'about/contact.html'

    def get_success_url(self):
        return reverse('contact_thanks')

    def form_valid(self, form):
        form.send_message()
        return super(ContactFormView, self).form_valid(form)


class ContactThanksView(TemplateView):
    """Display a thank-you page after the contact form is submitted"""
    template_name = 'about/contact_thanks.html'
