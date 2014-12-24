from datetime import date, datetime
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.text import slugify
from filebrowser.fields import FileBrowseField

__all__ = ['Review', 'Audition', 'ProductionCompany', 'Production', 'Play',
    'Venue', 'Address', 'ArtsNews', 'Festival', 'Reviewer', 'ExternalReview']

class Review(models.Model):
    """A written review of a production"""
    title = models.CharField(max_length=150, null=True, blank=True,
        help_text="If blank, defaults to 'Review: *production*'")

    cover_image = FileBrowseField(max_length=200, null=True, blank=True,
        format='image', directory='review_covers', help_text='Image to display '
        'at the top of the review and in the homepage feature area')

    production = models.ForeignKey('Production')
    reviewer = models.ForeignKey('Reviewer')
    content = models.TextField()

    lede = models.CharField(max_length=300, null=True, blank=True,
        help_text='Enter a brief (< 300 character) introduction to the review. '
        'If blank, the first 50 words of the content will be used on the '
        'homepage.')

    is_published = models.BooleanField(default=False, verbose_name='Published',
        help_text='If false, this review will not be visible on the site')

    published_on = models.DateTimeField(null=True, blank=True,
        help_text='Stores the time when this review was published.')

    slug = models.SlugField(help_text='This field will be used in the URL for '
        "this review's page.")

    class Meta:
        ordering = ['-published_on']

    def get_title(self):
        title = self.title if self.title else 'Review: %s' % self.production
        return title

    def get_slug(self):
        return slugify(unicode(self.get_title()))[:50]

    def publish(self):
        self.is_published = True
        self.published_on = datetime.now()
        self.save()

    def unpublish(self):
        self.is_published = False
        self.save()

    def save(self, *args, **kwargs):
        self.title = self.get_title()
        self.slug = self.get_slug()
        return super(Review, self).save(**kwargs)

    def get_absolute_url(self):
        return reverse('review_detail', kwargs={'slug':self.slug})

    def __unicode__(self):
        return unicode(self.get_title())


class AuditionManager(models.Manager):
    def filter_upcoming(self):
        """Return ongoing or upcoming auditions"""
        today = timezone.now()
        upcoming = self.filter(
            Q(end_date__isnull=False, end_date__gte=today) | 
            Q(end_date__isnull=True, start_date__gte=today)
        ).order_by('start_date')
        return upcoming


class Audition(models.Model):
    """Represents a casting call"""
    title = models.CharField(max_length=150, null=True, blank=True,
        help_text="If none, defaults to 'Audition for *play*, by *company*'")

    production_company = models.ForeignKey('ProductionCompany',
        null=True, blank=True, help_text='The production company conducting '
        'the audition.')

    play = models.ForeignKey('Play', null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True,
        help_text='Leave blank if the auditions last a single day')

    event_details = models.TextField(null=True, blank=True,
        help_text='Use this field to provide additional event information, '
        'such as where the event occurs, at what time, or any relevant '
        'contact information.')

    content = models.TextField(null=True, blank=True,
        help_text='Use this field to provide information not directly '
        'relevant to the event, such as available roles, required experience '
        'or additional information about the production.')

    poster = FileBrowseField(max_length=200, null=True, blank=True,
        format='image', directory='posters')

    slug = models.SlugField(help_text='This field will be used in the URL for '
        "this auditions's detail page.")

    objects = AuditionManager()

    def get_title(self):
        """
        Assemble and return a string identifying this audition if a custom 
        title is not available
        """
        title = ''
        if self.title:
            title = self.title
        elif self.play and self.production_company:
            title = 'Audition for %s, by %s' % (
                self.play, self.production_company)
        elif self.play or self.production_company:
            title = 'Audition for %s' % (self.play or self.production_company)
        else:
            title = 'Audition'
        return unicode(title)

    def get_alt_description(self):
        """
        To be used if self.content is empty, this method will return a rough
        description of the record based on other field values
        """
        description = 'Audition'
        if self.play:
            description += ' for a role in %s' % self.play

        if self.production_company:
            description += ' with %s' % self.production_company

        description += ' on %s' % self.start_date.strftime('%b %d')
        if self.end_date:
            description += ' through %s' % self.end_date.strftime('%b %d')
        description += '.'

        return description

    def duration(self, date_format='%b. %d'):
        """
        Return a string representing the date range during which the audition
        is held. The dates will be formatted with date_format.
        """
        duration = self.start_date.strftime(date_format)
        if self.end_date:
            duration += ' - %s' % self.end_date.strftime(date_format)
        return duration

    def save(self, *args, **kwargs):
        self.title = self.get_title()
        self.slug = self.get_slug()
        return super(Audition, self).save(**kwargs)

    def get_slug(self):
        return slugify(unicode(self.get_title()))[:50]

    def get_absolute_url(self):
        return reverse('audition_detail', kwargs={'slug':self.slug})

    def __unicode__(self):
        return unicode(self.get_title)


class ProductionCompany(models.Model):
    """A company or theatre group -- those who put on the show """
    name = models.CharField(max_length=150)
    home_venues = models.ManyToManyField('Venue', null=True, blank=True,
        help_text='List any venues at which this company regularly performs.')

    description = models.TextField(null=True, blank=True,
        help_text="Provide any additional information, such as the company's "
        "history, goals, or charter.")

    contact_info = models.TextField(null=True, blank=True,
        verbose_name="Contact Information")

    company_site = models.URLField(null=True, blank=True,
        verbose_name='Company Website', help_text="Enter the full URL to the "
        "company's website.")

    slug = models.SlugField(help_text='This field will be used in the URL for '
        "this company's detail page.")

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'production companies'

    def get_absolute_url(self):
        return reverse('production_company', kwargs={'slug':self.slug})

    def __unicode__(self):
        return unicode(self.name)


class ProductionManager(models.Manager):
    def filter_in_range(self, start_date, end_date):
        """Return Productions occurring in range [start_date, end_date]"""
        return self.filter(
            Q(start_date__gte=start_date, start_date__lte=end_date) |
            Q(start_date__lte=start_date, end_date__isnull=False,
                end_date__gte=start_date))

    def filter_current(self):
        """Return Productions that are occuring today """
        today = date.today()
        return self.filter(Q(start_date__lte=today),
            Q(end_date__gte=today) | Q(end_date__isnull=True))


class Production(models.Model):
    """A company's interpretation & performance of a play"""
    play = models.ForeignKey('Play')
    production_company = models.ForeignKey('ProductionCompany', null=True,
        blank=True, help_text='Leave this field blank if the production '
        'is a one-person show.')

    venue = models.ForeignKey('Venue')
    start_date = models.DateField(verbose_name='Date of first performance')

    end_date = models.DateField(null=True, blank=True, 
        verbose_name='Date of last performance', help_text='Leave blank for '
        'productions with a single performance.')

    event_details = models.TextField(null=True, blank=True,
        help_text='Provide additional event information, such as a weekly '
        'schedule, ticket prices, or venue details.')

    description = models.TextField(null=True, blank=True)
    poster = FileBrowseField(max_length=200, null=True, blank=True, 
        format='image', directory='posters')

    slug = models.SlugField(help_text='This field will be used in the URL for '
        "this production's detail page.")

    objects = ProductionManager()

    @property
    def title(self):
        title = unicode(self.play)
        if self.production_company:
            title += ' by %s' % self.production_company
        return title

    def save(self, *args, **kwargs):
        self.slug = self.get_slug()
        return super(Production, self).save(**kwargs)

    def duration(self, date_format='%b. %d', conjuction='-'):
        """
        Return a string representing the date range during which the production
        occurs. The dates will be formatted with date_format.
        """
        duration = self.start_date.strftime(date_format)
        if self.end_date:
            duration += ' %s %s' % (
                conjuction, self.end_date.strftime(date_format))
        return duration

    def detailed_duration(self):
        """Alias to duration with detailed date_format and conjuction args"""
        return self.duration(date_format='%B %d, %Y', conjuction='through')

    def get_slug(self):
        """Return a unique slug for this Production"""
        slug = slugify(unicode(self.title))
        previous_productions = Production.objects.filter(
            slug=slug).exclude(pk=self.pk).count()
        if previous_productions:
            slug += str(previous_productions)
        return slug

    def get_absolute_url(self):
        return reverse('production_detail', kwargs={'slug':self.slug})

    def __unicode__(self):
        return unicode(self.title)


class Play(models.Model):
    """Represents the script of play"""
    title = models.CharField(max_length=150)
    playwright = models.CharField(max_length=80, null=True, blank=True)
    synopsis = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['title']

    def __unicode__(self):
        return unicode(self.title)


class Venue(models.Model):
    """A location in which a production can be performed"""
    name = models.CharField(max_length=80)
    address = models.OneToOneField('Address')
    map_url = models.URLField(null=True, blank=True)
    slug = models.SlugField(help_text='This field will be used in the URL for '
        "this venue's detail page.")

    class Meta:
        ordering = ['name']

    def get_absolute_url(self):
        return reverse('venue_detail', kwargs={'slug':self.slug})

    def __unicode__(self):
        return unicode(self.name)


class Address(models.Model):
    """The physical address of a venue"""
    line_1 = models.CharField(max_length=150)
    line_2 = models.CharField(max_length=150, null=True, blank=True)
    city = models.CharField(max_length=80)
    zip_code = models.CharField(max_length=10)

    class Meta:
        ordering = ['line_1']
        verbose_name_plural = 'addresses'

    def __unicode__(self):
        address_str = '%s, ' % self.line_1
        if self.line_2:
            address_str += ' %s, ' % self.line_2
        return u'%s %s TX, %s' % (address_str, self.city, self.zip_code)


class ArtsNews(models.Model):
    """A news item of interest to the theatre world"""
    title = models.CharField(max_length=150)
    content = models.TextField(null=True, blank=True)

    external_url = models.URLField(null=True, blank=True,
        help_text='If this news item links to an external location, provide '
        'the full URL.')

    created_on = models.DateTimeField(auto_now_add=True)

    slug = models.SlugField(help_text='This field will be used in the URL for '
        "this news item's detail page.")

    class Meta:
        ordering = ['-created_on']
        verbose_name_plural = 'arts news items'

    def get_absolute_url(self):
        url = self.external_url \
            if self.external_url \
            else reverse('news_detail', kwargs={'slug':self.slug})
        return url

    def __unicode__(self):
        title = (self.title 
            if len(self.title) < 20 
            else '%s...' % self.title[:20])
        return u'%s: %s' % (self.created_on.strftime('%m/%d/%y'), title)


class Festival(models.Model):
    """A collection of productions, plays, or companies grouped chronologically"""
    title = models.CharField(max_length=80, verbose_name='Festival Name',
        help_text='Yearly festivals should be distinguished by number or year')

    description = models.TextField(null=True, blank=True)
    productions = models.ManyToManyField('Production', null=True, blank=True,
        help_text='For any productions listed here, do not include the '
        'corresponding companies, plays, or venues in subsequent fields.')

    plays = models.ManyToManyField('Play', null=True, blank=True,
        help_text='List plays for which no addition production information '
        'is available.')

    production_companies = models.ManyToManyField('ProductionCompany',
        null=True, blank=True, help_text='List involved companies whose '
        'productions are unknown.')

    venues = models.ManyToManyField('Venue', null=True, blank=True,
        help_text='List any involved venues whose performances are unknown.')

    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True,
        help_text='Leave blank for one-day festivals.')

    slug = models.SlugField(help_text='This field will be used in the URL for '
        "this review's page.")

    def __unicode__(self):
        return unicode(self.title)


class ReviewerManager(models.Manager):
    def filter_active(self):
        """Return Reviewers who have published reviews recently"""
        # get reviews of the past 6 months, and extract their reviewers
        six_months_ago = date.today() - timedelta(months=6)
        recent_reviews = Review.objects.filter(published_on__gte=six_months_ago)
        recent_reviewers = recent_reviews.values_list('reviewer').distinct()

        # sort the reviews by the number of reviews they have published
        return recent_reviewers.annotate(
            reviews_count=Count('review_set')).order_by(reviews_count)

    def filter_inactive(self):
        """Return Reviewers who have not published reviews recently"""
        recent_reviewer_ids = self.filter_active().values_list('id', flat=True)
        return self.exclude(id__in=recent_reviewer_ids).order_by('last_name')


class Reviewer(models.Model):
    """Contains bio information for those who write reviews"""
    user = models.OneToOneField('auth.User', null=True, blank=True)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    headshot = FileBrowseField(max_length=200, null=True, blank=True,
        format='image', directory='headshots')
    bio = models.TextField(null=True, blank=True)

    objects = ReviewerManager()

    @property
    def full_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    @property
    def review_count(self):
        return self.review_set.count()

    def __unicode__(self):
        return unicode(self.full_name)


class ExternalReview(models.Model):
    """Contains a link to a review provided by an external source"""
    review_url = models.URLField()
    source_name = models.CharField(max_length=100, help_text='Provide the name '
        'of the reviewer or the group that published it.')
    production = models.ForeignKey(Production)

    def __unicode__(self):
        return u"%s's review of %s" % (self.source_name, self.production)
