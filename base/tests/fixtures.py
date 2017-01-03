import factory
from django.utils import timezone
from django.utils.text import slugify

from base import models


class AddressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Address

    line_1 = '123 Test St.'
    city = 'Austin'
    zip_code = '78730'


class ArtsNewsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ArtsNews

    title = 'Test News'
    slug = factory.LazyAttributeSequence(
        lambda o, n: '{slug}-{n}'.format(slug=slugify(unicode(o.title)), n=n)
    )
    created_on = factory.LazyFunction(timezone.now)


class AuditionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Audition

    start_date = factory.LazyFunction(timezone.now)
    slug = factory.Sequence(lambda n: 'test-audition-{}'.format(n))


class NewsSlideshowImageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.NewsSlideshowImage

    news = factory.SubFactory(ArtsNewsFactory)


class PlayFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Play

    title = 'Test Play'


class VenueFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Venue

    name = 'Test Venue'
    address = factory.SubFactory(AddressFactory)
    slug = factory.LazyAttributeSequence(
        lambda o, n: '{slug}-{n}'.format(slug=slugify(unicode(o.name)), n=n)
    )


class ProductionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Production

    start_date = factory.LazyFunction(timezone.now)
    play = factory.SubFactory(PlayFactory)
    venue = factory.SubFactory(VenueFactory)
    slug = factory.Sequence(lambda n: 'production-{n}')


class ExternalReviewFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ExternalReview

    review_url = 'http://www.ctxlivetheatre.com'
    source_name = 'Austin Statesman'
    production = factory.SubFactory(ProductionFactory)


class ProductionCompanyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ProductionCompany

    name = 'Test Company'
    slug = factory.LazyAttributeSequence(
        lambda o, n: '{slug}-{n}'.format(slug=slugify(unicode(o.name)), n=n)
    )


class ReviewerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Reviewer

    first_name = 'Jane'
    last_name = 'Smith'


class ReviewFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Review

    production = factory.SubFactory(ProductionFactory)
    reviewer = factory.SubFactory(ReviewerFactory)
    content = 'This is the review content.'
    slug = factory.Sequence(lambda n: 'review-{}'.format(n))


class ProductionPosterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ProductionPoster

    production = factory.SubFactory(ProductionFactory)
