from django.db import models

__all__ = ['Review', 'Audition', 'ProductionCompany', 'Production', 'Play',
    'Venue', 'Address', 'ArtsNews', 'Festival']

class Review(models.Model):
    """A written review of a production"""
    title = models.CharField(max_length=150, null=True, blank=True,
        help_text="If none, defaults to 'Review: <production>'")

    cover_image = models.ImageField(null=True, blank=True,
        help_text='Image to display at the top of the review and in the '
        'homepage feature area')

    production = models.ForeignKey('Production')
    content = models.TextField()

    is_published = models.BooleanField(default=False, verbose_name='Published',
        help_text='If false, this review will not be visible on the site')

    def get_title(self):
        title = self.title if self.title else 'Review: %s' % self.production
        return title

    def __unicode__(self):
        return unicode(self.get_title)


class AuditionManager(models.Manager):
    def filter_upcoming(self):
        """Return ongoing or upcoming auditions"""
        today = timezone.today()
        upcoming = self.filter(
            Q(end_date__isnull=False, end_date__gte=today) | 
            Q(end_date__isnull=True, start_date__gte=today)
        ).order_by('start_date')
        return upcoming


class Audition(models.Model):
    """Represents a casting call"""
    title = models.CharField(max_length=150, null=True, blank=True,
        help_text="If none, defaults to 'Audition for <play>, by <company>'")

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

    def __unicode(self):
        return unicode(self.get_title)


class ProductionCompany(models.Model):
    """A company or theatre group -- those who put on the show """
    name = models.CharField(max_length=150)
    home_venue = models.ManyToManyField('Venue', null=True, blank=True,
        help_text='List any venues at which this company regularly performs.')

    description = models.TextField(null=True, blank=True,
        help_text="Provide any additional information, such as the company's "
        "history, goals, or charter.")

    contact_info = models.TextField(null=True, blank=True,
        verbose_name="Contact Information")

    company_site = models.URLField(null=True, blank=True,
        verbose_name='Company Website', help_text="Enter the full URL to the "
        "company's website.")

    def __unicode__(self):
        return unicode(self.name)


class Production(models.Model):
    """A company's interpretation & performance of a play"""
    play = models.ForeignKey('Play')
    production_company = models.ForeignKey('ProductionCompany')
    venue = models.ForeignKey('Venue')
    start_date = models.DateField(verbose_name='Date of first performance')

    end_date = models.DateField(null=True, blank=True, 
        verbose_name='Date of last performance', help_text='Leave blank for '
        'productions with a single performance.')

    event_details = models.TextField(null=True, blank=True,
        help_text='Provide additional event information, such as a weekly '
        'schedule, ticket prices, or venue details.')

    description = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return u'%s by %s' % (self.play, self.production_company)


class Play(models.Model):
    """Represents the script of play"""
    title = models.CharField(max_length=150)
    playwright = models.CharField(max_length=80, null=True, blank=True)
    synopsis = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return unicode(title)


class Venue(models.Model):
    """A location in which a production can be performed"""
    name = models.CharField(max_length=80)
    address = models.OneToOneField('Address')
    map_url = models.URLField(null=True, blank=True)

    def __unicode__(self):
        return unicode(name)


class Address(models.Model):
    """The physical address of a venue"""
    line_1 = models.CharField(max_length=150)
    line_2 = models.CharField(max_length=150, null=True, blank=True)
    city = models.CharField(max_length=80)
    zip_code = models.CharField(max_length=10)

    def __unicode__(self):
        return u'%s, %s, %s TX, %s' % (
            self.line_1, self.line2, self.city, self.zip_code)


class ArtsNews(models.Model):
    """A news item of interest to the theatre world"""
    title = models.CharField(max_length=150)
    content = models.TextField()

    external_url = models.URLField(null=True, blank=True,
        help_text='If this news item links to an external location, provide '
        'the full URL.')

    created_on = models.DateTimeField(auto_now_add=True)

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

    def __unicode__(self):
        return unicode(self.title)
