from datetime import timedelta
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from filebrowser.fields import FileBrowseField

__all__ = (
    'Review', 'Audition', 'ProductionCompany', 'Production', 'Play',
    'Venue', 'Address', 'ArtsNews', 'Reviewer', 'ExternalReview',
    'NewsSlideshowImage', 'ProductionPoster'
)


class Review(models.Model):
    """A written review of a production"""
    title = models.CharField(
        max_length=150, null=True, blank=True,
        help_text="If blank, defaults to 'Review: *production*'"
    )

    cover_image = FileBrowseField(
        max_length=200, null=True, blank=True,
        format='image', directory='review_covers', help_text='Image to display '
        'at the top of the review and in the homepage feature area'
    )

    production = models.ForeignKey('Production', on_delete=models.CASCADE)
    reviewer = models.ForeignKey('Reviewer', on_delete=models.CASCADE)
    content = models.TextField()

    lede = models.CharField(
        max_length=300, null=True, blank=True,
        help_text='Enter a brief (< 300 character) introduction to the review. '
        'If blank, the first 50 words of the content will be used on the '
        'homepage.'
    )

    is_published = models.BooleanField(
        default=False, verbose_name='Published',
        help_text='If false, this review will not be visible on the site'
    )

    published_on = models.DateTimeField(
        null=True, blank=True,
        help_text='Stores the time when this review was published.'
    )

    slug = models.SlugField(
        help_text="This field will be used in the URL for this review's page."
    )

    class Meta:
        ordering = ['-published_on']

    def get_title(self):
        title = self.title if self.title else u'Review: %s' % self.production
        return title

    def get_slug(self):
        if self.published_on is None:
            published_text = 'unpublished'
        else:
            published_text = self.published_on.strftime('%Y%m%d')
        slug = u'{published_date}-{title}'.format(
            published_date=published_text,
            title=self.get_title(),
        )
        return slugify(slug)[:50]

    def publish(self):
        self.is_published = True
        self.published_on = timezone.now()
        self.save()

    def unpublish(self):
        self.is_published = False
        self.save()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.title = self.get_title()
        self.slug = self.get_slug()
        if self.is_published and not self.published_on:
            self.published_on = timezone.now()
        return super(Review, self).save(**kwargs)

    def get_absolute_url(self):
        return reverse('review_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.get_title()


class DaysBase(models.Model):
    """Abstract base class to handle event object that occurs on certain days"""
    start_date = models.DateField(verbose_name='Date of first event.')
    end_date = models.DateField(
        null=True, blank=True, verbose_name='Date of last event.',
        help_text='Leave blank for events that last only a single day.'
    )
    on_monday = models.BooleanField(
        default=False, verbose_name='Occurs on Monday')
    on_tuesday = models.BooleanField(
        default=False, verbose_name='Occurs on Tuesday')
    on_wednesday = models.BooleanField(
        default=False, verbose_name='Occurs on Wednesday')
    on_thursday = models.BooleanField(
        default=False, verbose_name='Occurs on Thursday')
    on_friday = models.BooleanField(
        default=False, verbose_name='Occurs on Friday')
    on_saturday = models.BooleanField(
        default=False, verbose_name='Occurs on Saturday')
    on_sunday = models.BooleanField(
        default=False, verbose_name='Occurs on Sunday')

    days = (
        {'abbrev': 'M', 'name': 'Monday', 'boolean_field': 'on_monday'},
        {'abbrev': 'T', 'name': 'Tuesday', 'boolean_field': 'on_tuesday'},
        {'abbrev': 'W', 'name': 'Wednesday', 'boolean_field': 'on_wednesday'},
        {'abbrev': 'Th', 'name': 'Thursday', 'boolean_field': 'on_thursday'},
        {'abbrev': 'F', 'name': 'Friday', 'boolean_field': 'on_friday'},
        {'abbrev': 'Sat', 'name': 'Saturday', 'boolean_field': 'on_saturday'},
        {'abbrev': 'Sun', 'name': 'Sunday', 'boolean_field': 'on_sunday'},
    )

    class Meta:
        abstract = True

    def get_last_sequential_day_index(
            self, start_on=0, wrap=True, stop_before=len(days)
    ):
        """
        Returns index of the final day in a sequence when the event occurs

        start_on:   index of the day of the week to start the sequence
        wrap:       boolean indicating if earlier days can be considered
        stop_before:index of the day that must end the sequence
        """
        # check days following start_on until we find one during which the event
        # doesn't occur, or we reach the end of the allowable sequence
        end_on = None
        for offset, day_tuple in enumerate(self.days[start_on:stop_before]):
            if not getattr(self, day_tuple['boolean_field'], False):
                break
            end_on = start_on + offset

        # if wrapping, find the final day of a sequence that starts on monday,
        # and ends on start_on (at the latest)
        if wrap and start_on > 0 and end_on == len(self.days)-1:
            end_on_next_week = self.get_last_sequential_day_index(
                wrap=False, stop_before=start_on)
            end_on = (
                end_on_next_week
                if end_on_next_week is not None
                else end_on
            )

        return end_on

    def _week_booleans(self):
        """Return a list of booleans, indicating which days the event occurs"""
        week = []
        for day in self.days:
            week.append(getattr(self, day['boolean_field'], False))
        return week

    def has_weekly_schedule(self):
        """Return boolean indicate if any day-specific field has been marked"""
        return any(self._week_booleans())

    def get_verbose_week_description(self):
        return self.get_week_description(verbose=True)

    def get_week_description(self, verbose=False):
        """Return a string describing when the event occurs"""
        description_key = 'name' if verbose else 'abbrev'
        if verbose and self.end_date:
            pluralize = self.end_date - self.start_date > timedelta(days=7)
        else:
            pluralize = False
        week = self._week_booleans()
        if all(week):
            return u'All week'

        # get all days & sequences when event occurs. Start from first day when
        # the even doesn't occur when week-wrapping sequences are needed
        start_on = week.index(False) if self.on_sunday else 0
        description = ''
        described = []
        for day_idx in range(start_on, len(self.days)):
            # check if day has already been described as part of a sequence
            if day_idx in described:
                continue

            # ignore day if event doesn't occur
            day_tuple = self.days[day_idx]
            if not getattr(self, day_tuple['boolean_field'], False):
                continue

            # try to retrieve end of sequence, create appropriate description
            sequence_end = self.get_last_sequential_day_index(start_on=day_idx)
            if sequence_end == day_idx:
                description += '{0}{1}, '.format(
                    self.days[day_idx][description_key],
                    's' if pluralize else '')
                described.append(day_idx)
            else:
                sequence_description = '{day1}{plural}-{day2}{plural}, '.format(
                    day1=self.days[day_idx][description_key],
                    day2=self.days[sequence_end][description_key],
                    plural='s' if pluralize else '')
                description += sequence_description
                if day_idx < sequence_end:
                    described += range(day_idx, sequence_end+1)
                else:
                    described += range(day_idx, len(self.days))
                    described += (
                        range(0, sequence_end)
                        if sequence_end > 0 else [0]
                    )

        return description.rstrip(', ')


class AuditionManager(models.Manager):
    def filter_upcoming(self):
        """Return ongoing or upcoming auditions"""
        today = timezone.now()
        upcoming = self.filter(
            Q(end_date__isnull=False, end_date__gte=today)
            | Q(end_date__isnull=True, start_date__gte=today)
        ).order_by('start_date')
        return upcoming


class Audition(models.Model):
    """Represents a casting call"""
    title = models.CharField(
        max_length=150, null=True, blank=True,
        help_text="If none, defaults to 'Auditions for *play*, by *company*'")

    production_company = models.ForeignKey(
        'ProductionCompany',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        help_text='The production company conducting the audition.'
    )

    play = models.ForeignKey('Play', null=True, blank=True, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(
        null=True, blank=True,
        help_text='Leave blank if the auditions last a single day')

    event_details = models.TextField(
        null=True, blank=True,
        help_text='Use this field to provide additional event information, '
        'such as where the event occurs, at what time, or any relevant '
        'contact information.')

    content = models.TextField(
        null=True, blank=True,
        help_text='Use this field to provide information not directly '
        'relevant to the event, such as available roles, required experience '
        'or additional information about the production.')

    poster = FileBrowseField(
        max_length=200, null=True, blank=True,
        format='image', directory='posters')

    slug = models.SlugField(
        help_text='This field will be used in the URL for '
        "this auditions's detail page.")

    created_on = models.DateTimeField(auto_now_add=True)
    created_on.editable = True  # force editable while migrating old data

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
            title = 'Auditions for %s, by %s' % (
                self.play, self.production_company)
        elif self.play or self.production_company:
            title = 'Auditions for %s' % (self.play or self.production_company)
        else:
            title = 'Auditions'
        return title

    def get_alt_description(self):
        """
        To be used if self.content is empty, this method will return a rough
        description of the record based on other field values
        """
        description = 'Auditions'
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

        # add the year if it is not included by date_format
        if self.start_date.year != timezone.now().year and 'y' not in date_format.lower():
            duration += ' (%s)' % (self.start_date.year)
        return duration

    def save(self, *args, **kwargs):
        if not self.pk:
            self.title = self.get_title()
        self.slug = self.get_slug()
        return super(Audition, self).save(**kwargs)

    def get_slug(self):
        slug = u'{start_date}-{title}'.format(
            start_date=self.start_date.strftime('%Y%m%d'),
            title=self.get_title(),
        )
        return slugify(slug)[:50]

    def get_absolute_url(self):
        return reverse('audition_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.get_title()


class ProductionCompanyManager(models.Manager):
    def filter_active(self):
        """Return ProductionCompany objects that been active in the past year"""
        one_year_ago = timezone.now() - timedelta(days=365)
        return ProductionCompany.objects.filter(
            Q(production__start_date__gte=one_year_ago) |
            Q(audition__start_date__gte=one_year_ago)).distinct()


class ProductionCompany(models.Model):
    """A company or theatre group -- those who put on the show """
    name = models.CharField(max_length=150)
    home_venues = models.ManyToManyField(
        'Venue', blank=True,
        help_text='List any venues at which this company regularly performs.')

    description = models.TextField(
        null=True, blank=True,
        help_text="Provide any additional information, such as the company's "
        "history, goals, or charter.")

    contact_info = models.TextField(
        null=True, blank=True,
        verbose_name="Contact Information")

    company_site = models.URLField(
        null=True, blank=True, verbose_name='Company Website',
        help_text="Enter the full URL to the company's website.")

    logo = FileBrowseField(
        max_length=200, null=True, blank=True,
        format='image', directory='logos')

    slug = models.SlugField(
        help_text='This field will be used in the URL for '
        "this company's detail page.")

    objects = ProductionCompanyManager()

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'production companies'

    @property
    def review_set(self):
        """Return the reviews related to this company's productions"""
        return Review.objects.filter(production__production_company=self)

    def get_related_news(self):
        """Return news related to this company or this company's productions"""
        related_news = ArtsNews.objects.filter(
            Q(related_company=self) |
            Q(related_production__production_company=self)).distinct()
        return related_news

    def published_reviews(self):
        """Return published reviews for this company's productions"""
        return Review.objects.filter(
            production__production_company=self, is_published=True)

    def get_absolute_url(self):
        return reverse('production_company', kwargs={'slug': self.slug})

    def __str__(self):
        return self.name


class ProductionManager(models.Manager):
    def filter_in_range(self, start_date, end_date):
        """Return Productions occurring in range [start_date, end_date]"""
        return self.filter(
            Q(start_date__gte=start_date, start_date__lte=end_date) |
            Q(start_date__lte=start_date, end_date__isnull=False,
                end_date__gte=start_date))

    def filter_current(self):
        """Return Productions that are occuring today """
        today = timezone.now()
        return self.filter(
            Q(Q(start_date__lte=today), Q(end_date__gte=today)) |
            Q(Q(start_date=today), Q(end_date__isnull=True))
        )


class Production(DaysBase):
    """A company's interpretation & performance of a play"""
    play = models.ForeignKey('Play', on_delete=models.CASCADE)
    production_company = models.ForeignKey(
        'ProductionCompany',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        help_text='Leave this field blank if the production is a one-person show.',
    )

    venue = models.ForeignKey('Venue', on_delete=models.CASCADE)

    event_details = models.TextField(
        null=True, blank=True,
        help_text='Provide additional event information, such as ticket prices '
        'or daily schedules. Do not include the venue, opening/closing dates, '
        'or company information.')

    description = models.TextField(null=True, blank=True)
    poster = FileBrowseField(
        max_length=200, null=True, blank=True, format='image',
        directory='posters', help_text='If this production has multiple '
        'posters, place the most relevant here. Add the others to the '
        'secondary posters formset.')

    slug = models.SlugField(
        help_text='This field will be used in the URL for '
        "this production's detail page.")

    created_on = models.DateTimeField(auto_now_add=True)
    created_on.editable = True  # force editable while migrating old data

    objects = ProductionManager()

    @property
    def title(self):
        title = self.play.title
        if self.production_company:
            title += u' by %s' % self.production_company
        return title

    def save(self, *args, **kwargs):
        self.slug = self.get_slug()
        return super(Production, self).save(**kwargs)

    def duration(self, date_format='%b. %d', conjuction='-', append_year=False):
        """
        Return a string representing the date range during which the production
        occurs. The dates will be formatted with date_format.
        """
        duration = self.start_date.strftime(date_format)
        if self.end_date:
            duration += ' %s %s' % (
                conjuction, self.end_date.strftime(date_format))

        # force inclusion of the year if production is old
        if not append_year:
            append_year = (
                self.start_date.year != timezone.now().year
                and 'y' not in date_format.lower())
        if append_year:
            duration += ', %s' % (self.start_date.year)
        return duration

    def semi_detailed_duration(self):
        """Alias to duration with full-name months and an appended year"""
        return self.duration(date_format='%B %d', append_year=True)

    def detailed_duration(self):
        """Alias to duration with detailed date_format and conjuction args"""
        return self.duration(date_format='%B %d, %Y')

    def published_reviews(self):
        """Return this production's published reviews"""
        return self.review_set.filter(is_published=True)

    def get_slug(self):
        """Return a unique slug for this Production"""
        slug = u'{start_date}-{title}'.format(
            start_date=self.start_date.strftime('%Y%m%d'),
            title=self.title,
        )
        return slugify(slug)[:50]

    def get_absolute_url(self):
        return reverse('production_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title


class Play(models.Model):
    """Represents the script of play"""
    title = models.CharField(max_length=150)
    playwright = models.CharField(max_length=80, null=True, blank=True)
    synopsis = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class VenueManager(models.Manager):
    def filter_cities(self):
        """Return a dictionary that categorizes venues by city"""
        cities = self.order_by('address__city').values_list(
            'address__city', flat=True).distinct()

        city_venues = {}
        for city in cities:
            city_venues[city] = self.filter(address__city=city)
        return city_venues

    def filter_active(self):
        """Return Venue objects that been active in the past year"""
        one_year_ago = timezone.now() - timedelta(days=365)
        return Venue.objects.filter(
            production__start_date__gte=one_year_ago).distinct()


class Venue(models.Model):
    """A location in which a production can be performed"""
    name = models.CharField(max_length=80)
    address = models.OneToOneField('Address', on_delete=models.CASCADE)
    map_url = models.URLField(null=True, blank=True)
    slug = models.SlugField(
        help_text='This field will be used in the URL for '
        "this venue's detail page.")

    objects = VenueManager()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Address(models.Model):
    """The physical address of a venue"""
    line_1 = models.CharField(max_length=150)
    line_2 = models.CharField(max_length=150, null=True, blank=True)
    city = models.CharField(max_length=80)
    zip_code = models.CharField(max_length=10)

    class Meta:
        ordering = ['line_1']
        verbose_name_plural = 'addresses'

    def __str__(self):
        address_str = '%s,' % self.line_1
        if self.line_2:
            address_str += ' %s,' % self.line_2
        return u'%s %s TX, %s' % (address_str, self.city, self.zip_code)


class ArtsNewsManager(models.Manager):
    def filter_media(self):
        """Return a list of all news items with feature media"""
        video_news = self.filter(video_embed__isnull=False).exclude(
            video_embed='')
        slideshow_news = self.filter(newsslideshowimage__isnull=False)

        # merge querysets into a list, ordered by created_on field
        media_news = sorted(
            list(video_news) + list(slideshow_news),
            key=lambda news: news.created_on,
            reverse=True)
        return media_news


class ArtsNews(models.Model):
    """A news item of interest to the theatre world"""
    title = models.CharField(max_length=150)
    content = models.TextField(
        null=True, blank=True, help_text='Add the main content of the news '
        'story here. Do not include any content from other fields or related '
        'objects (such as video embeds, slideshow images, or related '
        'production or company details).')

    is_job_opportunity = models.BooleanField(
        default=False,
        help_text='Check if this news item is about a job opportunity.')

    external_url = models.URLField(
        null=True, blank=True,
        help_text='If this news item links to an external location, provide '
        'the full URL.')

    video_embed = models.CharField(
        max_length=500, null=True, blank=True,
        help_text='If this story includes a video, enter the embed code here '
        'to feature it on the homepage. Be sure to remove any width and height '
        'attributes.')

    related_production = models.ForeignKey(
        Production,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        help_text='If appropriate, specify the production that this story addresses.',
    )

    related_company = models.ForeignKey(
        ProductionCompany,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        help_text='If appropriate, specify the production company that this story addresses.',
    )

    created_on = models.DateTimeField(auto_now_add=True)
    created_on.editable = True  # force editable while migrating old data

    slug = models.SlugField(
        help_text='This field will be used in the URL for '
        "this news item's detail page.")

    objects = ArtsNewsManager()

    class Meta:
        ordering = ['-created_on']
        verbose_name_plural = 'arts news items'

    def has_media(self):
        """Check if this news item has a video or images to be featured"""
        return self.video_embed or self.newsslideshowimage_set.exists()

    def save(self, *args, **kwargs):
        self.slug = self.get_slug()
        return super(ArtsNews, self).save(**kwargs)

    def get_slug(self):
        slug = u'{created_on}-{title}'.format(
            created_on=timezone.now().strftime('%Y%m%d'),
            title=self.title,
        )
        return slugify(slug)[:50]

    def get_absolute_url(self):
        url = (
            self.external_url
            if self.external_url
            else reverse('news_detail', kwargs={'slug': self.slug})
        )
        return url

    def __str__(self):
        title = (
            self.title
            if len(self.title) < 20
            else '%s...' % self.title[:20]
        )
        return u'%s: %s' % (self.created_on.strftime('%m/%d/%y'), title)


class ReviewerManager(models.Manager):
    def filter_active(self):
        """Return Reviewers who have published reviews recently"""
        six_months_ago = timezone.now() - timedelta(days=6*365/12)
        recent_reviewers = Reviewer.objects.filter(
            review__published_on__gte=six_months_ago)
        return recent_reviewers.distinct()

    def filter_inactive(self):
        """Return Reviewers who have not published reviews recently"""
        recent_reviewer_ids = self.filter_active().values_list('id', flat=True)
        return self.exclude(id__in=recent_reviewer_ids).order_by('last_name')


class Reviewer(models.Model):
    """Contains bio information for those who write reviews"""
    user = models.OneToOneField('auth.User', null=True, blank=True, on_delete=models.SET_NULL)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    headshot = FileBrowseField(
        max_length=200, null=True, blank=True,
        format='image', directory='headshots')
    bio = models.TextField(null=True, blank=True)

    objects = ReviewerManager()

    @property
    def full_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    @property
    def review_count(self):
        return self.review_set.count()

    def __str__(self):
        return self.full_name


class ExternalReview(models.Model):
    """Contains a link to a review provided by an external source"""
    review_url = models.URLField()
    source_name = models.CharField(
        max_length=100, help_text='Provide the name '
        'of the reviewer or the group that published it.')
    production = models.ForeignKey(Production, on_delete=models.CASCADE)

    def __str__(self):
        return u"%s's review of %s" % (self.source_name, self.production)


class SlideshowImage(models.Model):
    """Contains a single image; representing a portion of a slideshow"""
    image = FileBrowseField(max_length=200, format='image')
    order = models.IntegerField(
        default=0, help_text='Optional: set the order '
        'in which this image should be displayed.')

    class Meta:
        abstract = True

    def __str__(self):
        return self.image


class NewsSlideshowImage(SlideshowImage):
    """Represents a slideshow image tied a news story"""
    news = models.ForeignKey(ArtsNews, on_delete=models.CASCADE)

    class Meta:
        ordering = ['news', 'order']


class ProductionPoster(SlideshowImage):
    """Represents a secondary poster for a production"""
    production = models.ForeignKey(Production, on_delete=models.CASCADE)

    class Meta:
        ordering = ['production', 'order']
