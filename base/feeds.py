from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.utils import timezone

from base.models import Review, Production, Audition, ArtsNews

class AggregatedFeed(Feed):
    """An RSS feed displaying all major content items"""
    title = 'CTX Live Theatre'
    description = ('CTX Live Theatre is a project - or maybe no more than a '
        'hobby, bordering on a quiet obsession - devoted to supporting live '
        'narrative theatre in Central Texas.')
    link = '/'

    def items(self):
        """Return a sorted list of Productions, Auditions, News, and Reviews"""
        productions = Production.objects.all()
        auditions = Audition.objects.all()
        news = ArtsNews.objects.all()
        reviews = Review.objects.filter(is_published=True)
        aggregated = (list(productions) + list(auditions) + 
            list(news) + list(reviews))
        return sorted(aggregated, reverse=True, key=lambda item: item.created_on 
            if hasattr(item, 'created_on') else item.published_on)

    def item_title(self, object):
        return object.title

    def item_description(self, object):
        description = (object.content 
            if hasattr(object, 'content')
            else object.description)
        return description
        
    def item_pubdate(self, item):
        pubdate = timezone.now()
        if hasattr(item, 'created_on'):
            pubdate = item.created_on
        elif hasattr(item, 'published_on'):
            pubdate = item.published_on
        return pubdate

    def item_categories(self, item):
        categories = []
        if isinstance(item, Production):
            categories.append('Productions')
        elif isinstance(item, Review):
            categories.append('Reviews')
        elif isinstance(item, Audition):
            categories.append('Auditions')
        elif isinstance(item, ArtsNews):
            categories.append('News')
        return categories
