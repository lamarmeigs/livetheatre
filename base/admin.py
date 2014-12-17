from datetime import datetime
from django.contrib import admin
from django.db import models
from tinymce.widgets import TinyMCE

from base.models import *


class ReviewAdmin(admin.ModelAdmin):
    readonly_fields = ('is_published', 'published_on')
    prepopulated_fields = {'slug': ('title',)}
    actions_on_bottom = True
    save_on_top = True

    list_display = ('get_title', 'is_published')
    list_filter = ('is_published',)
    ordering = ('published_on',)

    search_fields = ['title', 'production__play__title',
        'production__production_company__name']
    actions = ['publish_reviews', 'unpublish_reviews']

    formfield_overrides = {
        models.TextField: {'widget': TinyMCE(attrs={'cols':80, 'rows':30})},
    }

    def publish_reviews(self, request, queryset):
        rows_updated = queryset.update(
            is_published=True, published_on=datetime.now())
        message = '%s review%s published.' % (
            rows_updated, '' if rows_updated == 1 else 's')
        self.message_user(request, message)

    def unpublish_reviews(self, request, queryset):
        rows_updated = queryset.update(is_published=False)
        message = '%s review%s unpublished.' % (
            rows_updated, '' if rows_updated == 1 else 's')
        self.message_user(request, message)


class AuditionAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    actions_on_bottom = True
    save_on_top = True

    list_display = ('title', 'start_date', 'end_date')
    ordering = ('start_date',)

    search_fields = ['title', 'production_company__name', 'play__title']

    formfield_overrides = {
        models.TextField: {'widget': TinyMCE(attrs={'cols':80, 'rows':30})},
    }


class ProductionCompanyAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    actions_on_bottom = True
    save_on_top = True

    list_display = ('name',)
    search_fields = ['name', 'company_site']

    formfield_overrides = {
        models.TextField: {'widget': TinyMCE(attrs={'cols':80, 'rows':30})},
    }


class ProductionAdmin(admin.ModelAdmin):
    exclude = ('slug',)
    actions_on_bottom = True
    save_on_top = True

    list_display = ('play', 'production_company', 'start_date', 'end_date')
    list_filter = ('play__title', 'production_company__name', 'venue__name')
    ordering = ('start_date',)

    search_fields = ['play__title', 'production_company__name', 'venue__name']

    formfield_overrides = {
        models.TextField: {'widget': TinyMCE(attrs={'cols':80, 'rows':30})},
    }


class PlayAdmin(admin.ModelAdmin):
    actions_on_bottom = True
    save_on_top = True

    list_display = ('title', 'playwright')
    search_fields = ['title', 'playwright']

    formfield_overrides = {
        models.TextField: {'widget': TinyMCE(attrs={'cols':80, 'rows':30})},
    }


class VenueAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    actions_on_bottom = True
    save_on_top = True

    list_display = ('name', 'address')
    list_filter = ('address__city',)

    search_fields = ['name', 'address__line_1', 'address__city']

    formfield_overrides = {
        models.TextField: {'widget': TinyMCE(attrs={'cols':80, 'rows':30})},
    }


class ArtsNewsAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    actions_on_bottom = True
    save_on_top = True

    list_display = ('title', 'created_on')
    ordering = ('created_on',)

    search_fields = ['title', 'external_url']

    formfield_overrides = {
        models.TextField: {'widget': TinyMCE(attrs={'cols':80, 'rows':30})},
    }


class FestivalAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    actions_on_bottom = True
    save_on_top = True

    list_display = ('title', 'start_date', 'end_date')
    ordering = ('start_date',)

    search_fields = ['title', 'productions__play__title',
        'productions__production_company__name', 'plays__title',
        'production_companies__title', 'venues__name']

    formfield_overrides = {
        models.TextField: {'widget': TinyMCE(attrs={'cols':80, 'rows':30})},
    }


admin.site.register(Review, ReviewAdmin)
admin.site.register(Audition, AuditionAdmin)
admin.site.register(ProductionCompany, ProductionCompanyAdmin)
admin.site.register(Production, ProductionAdmin)
admin.site.register(Play, PlayAdmin)
admin.site.register(Venue, VenueAdmin)
admin.site.register(ArtsNews, ArtsNewsAdmin)
admin.site.register(Festival, FestivalAdmin)
