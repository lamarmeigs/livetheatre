from django.conf.urls import patterns, url

from base import views, feeds

urlpatterns = patterns('',
    url(r'^$', views.HomepageView.as_view(), name='home'),

    # Review pages
    url(r'^reviews/$',
        views.ReviewListView.as_view(),
        name='reviews'),

    url(r'^reviews/(?P<slug>[-\w]+)/$',
        views.ReviewDetailView.as_view(),
        name='review_detail'),


    # Audition pages
    url(r'^auditions/$',
        views.UpcomingAuditionListView.as_view(),
        name='auditions'),

    url(r'^auditions/past/$',
        views.PastAuditionListView.as_view(),
        name='auditions_past'),

    url(r'^auditions/(?P<slug>[-\w]+)/$',
        views.AuditionDetailView.as_view(),
        name='audition_detail'),


    # Production Company pages
    url(r'^local_theatres/$',
        views.LocalTheatresView.as_view(),
        name='local_theatres'),

    url(r'^local_theatres/(?P<slug>[-\w]+)/$',
        views.ProductionCompanyView.as_view(),
        name='production_company'),

    url(r'^local_theatres/(?P<slug>[-\w]+)/reviews/$',
        views.CompanyReviewListView.as_view(),
        name='company_reviews'),

    url(r'^local_theatres/(?P<slug>[-\w]+)/auditions/$',
        views.CompanyAuditionListView.as_view(),
        name='company_auditions'),

    url(r'^local_theatres/(?P<slug>[-\w]+)/auditions/past/$',
        views.CompanyPastAuditionListView.as_view(),
        name='company_auditions_past'),

    url(r'^local_theatres/(?P<slug>[-\w]+)/productions/$',
        views.CompanyProductionListView.as_view(),
        name='company_productions'),

    url(r'^local_theatres/(?P<slug>[-\w]+)/news/$',
        views.CompanyNewsListView.as_view(),
        name='company_news'),


    # News pages
    url(r'^news/$',
        views.NewsListView.as_view(),
        name='news_list'),

    url(r'^news/(?P<slug>[-\w]+)/$',
        views.NewsDetailView.as_view(),
        name='news_detail'),


    # Production pages
    url(r'^productions/$',
        views.UpcomingPerformanceView.as_view(),
        name='productions_upcoming'),

    url(r'^productions/monthly/$',
        views.MonthPerformanceView.as_view(),
        name='productions_current_month'),

    url(r'^productions/monthly/(?P<year>\d{4})/(?P<month>\d{1,2})/$',
        views.MonthPerformanceView.as_view(),
        name='productions_monthly'),

    url(r'^productions/weekly/$',
        views.WeekPerformanceView.as_view(),
        name='productions_current_week'),

    url(r'^productions/weekly/(?P<start_date>\d{4}\d{2}\d{2})/$',
        views.WeekPerformanceView.as_view(),
        name='productions_weekly'),

    url(r'^productions/city/$',
        views.CityPerformanceView.as_view(),
        name='productions_city'),

    url(r'^productions/city/(?P<city>[-\w ]+)/$',
        views.CityPerformanceView.as_view(),
        name='productions_city'),

    url(r'^productions/(?P<slug>[-\w]+)/$',
        views.ProductionDetailView.as_view(),
        name='production_detail'),

    url(r'^productions/(?P<slug>[-\w]+)/news/$',
        views.ProductionNewsListView.as_view(),
        name='production_news'),


    # Venue pages
    url(r'^venues/$',
        views.VenueListView.as_view(),
        name='venues'),

    url(r'^venues/(?P<slug>[-\w]+)/productions/$',
        views.VenueProductionListView.as_view(),
        name='venue_productions'),


    # About pages
    url(r'^about/$',
        views.AboutView.as_view(),
        name='about'),
    url(r'^about/principles_services/$',
        views.PrinciplesServicesView.as_view(),
        name='principles_and_services'),
    url(r'^about/reviewers/$',
        views.ReviewerListView.as_view(),
        name='reviewers'),


    # RSS feeds
    url(r'^rss/all/$',
        feeds.AggregatedFeed(),
        name='aggregated_rss_feed')
)
