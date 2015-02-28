import random
import string
from django.utils import timezone
from django.utils.text import slugify

from base.models import (Play, Address, Venue, ArtsNews, Reviewer,
    ExternalReview, ProductionCompany, Production, Review, Audition,
    NewsSlideshowImage)

def random_string(length=10):
    return ''.join(
        random.choice(string.ascii_lowercase + ' ') for _ in range(length))

def make_play(**kwargs):
    if 'title' not in kwargs:
        kwargs['title'] = random_string().title()
    return Play.objects.create(**kwargs)

def make_address(**kwargs):
    fields = {
        'line_1': random_string(),
        'city': random_string(),
        'zip_code': random_string()}
    fields.update(**kwargs)
    return Address.objects.create(**fields)

def make_venue(**kwargs):
    if 'name' not in kwargs:
        kwargs['name'] = random_string()
    if 'address' not in kwargs:
        kwargs['address'] = make_address()
    if 'slug' not in kwargs:
        kwargs['slug'] = slugify(unicode(kwargs['name']))
    return Venue.objects.create(**kwargs)

def make_news(**kwargs):
    if 'title' not in kwargs:
        kwargs['title'] = random_string()
    if 'slug' not in kwargs:
        kwargs['slug'] = slugify(unicode(kwargs['title']))
    return ArtsNews.objects.create(**kwargs)

def make_reviewer(**kwargs):
    for required_field in ('first_name', 'last_name'):
        if required_field not in kwargs:
            kwargs[required_field] = random_string()
    return Reviewer.objects.create(**kwargs)

def make_production_company(**kwargs):
    if 'name' not in kwargs:
        kwargs['name'] = random_string()
    if 'slug' not in kwargs:
        kwargs['slug'] = slugify(unicode(kwargs['name']))
    return ProductionCompany.objects.create(**kwargs)

def make_production(**kwargs):
    if 'play' not in kwargs:
        kwargs['play'] = make_play()
    if 'venue' not in kwargs:
        kwargs['venue'] = make_venue()
    if 'start_date' not in kwargs:
        kwargs['start_date'] = timezone.now()
    if 'slug' not in kwargs:
        kwargs['slug'] = random_string()
    return Production.objects.create(**kwargs)

def make_external_review(**kwargs):
    if 'review_url' not in kwargs:
        kwargs['review_url'] = 'http://%s.com' % random_string()
    if 'production' not in kwargs:
        kwargs['production'] = make_production()
    return ExternalReview.objects.create(**kwargs)

def make_review(**kwargs):
    if 'production' not in kwargs:
        kwargs['production'] = make_production()
    if 'reviewer' not in kwargs:
        kwargs['reviewer'] = make_reviewer()
    if 'content' not in kwargs:
        kwargs['content'] = random_string()
    if 'slug' not in kwargs:
        kwargs['slug'] = random_string()
    return Review.objects.create(**kwargs)

def make_audition(**kwargs):
    if 'start_date' not in kwargs:
        kwargs['start_date'] = timezone.now()
    if 'slug' not in kwargs:
        kwargs['slug'] = random_string()
    return Audition.objects.create(**kwargs)

def make_news_slideshow_image(**kwargs):
    if 'news' not in kwargs:
        kwargs['news'] = make_news()
    return NewsSlideshowImage.objects.create(**kwargs)
