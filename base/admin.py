from django.contrib import admin
from django.db import models
from django.utils import timezone
from tinymce.widgets import TinyMCE

from base.models import (
    Address, ArtsNews, Audition, ExternalReview, NewsSlideshowImage, Play,
    Production, ProductionCompany, ProductionPoster, Review, Reviewer, Venue
)


class ReviewAdmin(admin.ModelAdmin):
    actions_on_bottom = True
    save_on_top = True

    exclude = ('slug',)
    list_display = ('get_title', 'is_published', 'published_on')
    list_filter = ('is_published',)
    ordering = ('published_on',)

    search_fields = [
        'title', 'production__play__title',
        'production__production_company__name']
    autocomplete_fields = ['production']
    actions = ['publish_reviews', 'unpublish_reviews']

    formfield_overrides = {
        models.TextField: {'widget': TinyMCE(attrs={'cols': 80, 'rows': 30})},
    }

    def publish_reviews(self, request, queryset):
        rows_updated = queryset.update(
            is_published=True, published_on=timezone.now())
        message = '%s review%s published.' % (
            rows_updated, '' if rows_updated == 1 else 's')
        self.message_user(request, message)

    def unpublish_reviews(self, request, queryset):
        rows_updated = queryset.update(is_published=False)
        message = '%s review%s unpublished.' % (
            rows_updated, '' if rows_updated == 1 else 's')
        self.message_user(request, message)


class AuditionAdmin(admin.ModelAdmin):
    actions_on_bottom = True
    save_on_top = True

    exclude = ('slug',)
    list_display = ('title', 'start_date', 'end_date')
    ordering = ('start_date',)

    search_fields = ['title', 'production_company__name', 'play__title']
    autocomplete_fields = ['play', 'production_company']

    formfield_overrides = {
        models.TextField: {'widget': TinyMCE(attrs={'cols': 80, 'rows': 30})},
    }


class ProductionCompanyAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    actions_on_bottom = True
    save_on_top = True

    list_display = ('name',)
    search_fields = ['name', 'company_site']

    formfield_overrides = {
        models.TextField: {'widget': TinyMCE(attrs={'cols': 80, 'rows': 30})},
    }


class ProductionPosterInline(admin.TabularInline):
    model = ProductionPoster
    extra = 3
    verbose_name = 'Secondary Poster'
    verbose_name_plural = 'Secondary Posters'


class ProductionAdmin(admin.ModelAdmin):
    exclude = ('slug',)
    actions_on_bottom = True
    save_on_top = True

    list_display = ('play', 'production_company', 'start_date', 'end_date')
    list_filter = ('play__title', 'production_company__name', 'venue__name')
    ordering = ('start_date',)

    search_fields = ['play__title', 'production_company__name', 'venue__name']
    autocomplete_fields = ['play', 'production_company', 'venue']

    formfield_overrides = {
        models.TextField: {'widget': TinyMCE(attrs={'cols': 80, 'rows': 30})},
    }
    fieldsets = (
        (None, {
            'fields': ('play', 'production_company', 'venue')
        }),
        ('Schedule Information', {
            'description': (
                'Please provide the schedule for this production. '
                'Provide specific days only if the weekly schedule is '
                'explicitly stated and consistent.'
            ),
            'fields': (
                'start_date', 'end_date', 'on_monday', 'on_tuesday',
                'on_wednesday', 'on_thursday', 'on_friday', 'on_saturday',
                'on_sunday', 'event_details'
            ),
        }),
        ('Description & Poster', {'fields': ('description', 'poster')}),
        (None, {'fields': ('created_on',)})
    )
    inlines = [ProductionPosterInline]


class PlayAdmin(admin.ModelAdmin):
    actions_on_bottom = True
    save_on_top = True

    list_display = ('title', 'playwright')
    search_fields = ['title', 'playwright']

    formfield_overrides = {
        models.TextField: {'widget': TinyMCE(attrs={'cols': 80, 'rows': 30})},
    }


class VenueAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    actions_on_bottom = True
    save_on_top = True

    list_display = ('name', 'address')
    list_filter = ('address__city',)

    search_fields = ['name', 'address__line_1', 'address__city']
    autocomplete_fields = ['address']

    formfield_overrides = {
        models.TextField: {'widget': TinyMCE(attrs={'cols': 80, 'rows': 30})},
    }


class NewsSlideshowImageInline(admin.TabularInline):
    model = NewsSlideshowImage
    extra = 3


class ArtsNewsAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    actions_on_bottom = True
    save_on_top = True

    list_display = ('title', 'created_on')
    ordering = ('created_on',)

    search_fields = ['title', 'external_url']
    autocomplete_fields = ['related_production', 'related_company']

    formfield_overrides = {
        models.TextField: {'widget': TinyMCE(attrs={'cols': 80, 'rows': 30})},
    }

    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'created_on', 'slug')
        }),
        ('Related Objects', {
            'description': (
                'Select the items that are the subject of the '
                'news story. Excepts of these items will be displayed on the '
                "story's detail page. NOTE: an associated production takes "
                'priority over an associated company.'
            ),
            'fields': ('related_production', 'related_company'),
        }),
        ('Additional Media', {
            'description': (
                'Provide any additional media for this story. '
                'Additional fields for slideshow images are below.'
            ),
            'fields': ('is_job_opportunity', 'external_url', 'video_embed',)
        })
    )
    inlines = [NewsSlideshowImageInline]


class ReviewerAdmin(admin.ModelAdmin):
    actions_on_bottom = True
    save_on_top = True

    list_display = ('full_name', 'review_count')

    formfield_overrides = {
        models.TextField: {'widget': TinyMCE(attrs={'cols': 80, 'rows': 30})},
    }


class ExternalReviewAdmin(admin.ModelAdmin):
    actions_on_bottom = True
    save_on_top = True

    list_display = ('production', 'source_name', 'review_url')
    search_fields = [
        'production__play__title', 'source_name', 'review_url',
        'production__production_company__name']
    autocomplete_fields = ['production']


class AddressAdmin(admin.ModelAdmin):
    search_fields = ('line_1', 'line_2', 'city', 'zip_code')


admin.site.register(Review, ReviewAdmin)
admin.site.register(Audition, AuditionAdmin)
admin.site.register(ProductionCompany, ProductionCompanyAdmin)
admin.site.register(Production, ProductionAdmin)
admin.site.register(Play, PlayAdmin)
admin.site.register(Venue, VenueAdmin)
admin.site.register(ArtsNews, ArtsNewsAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Reviewer, ReviewerAdmin)
admin.site.register(ExternalReview, ExternalReviewAdmin)
