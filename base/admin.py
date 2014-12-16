from datetime import datetime
from django.contrib import admin

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

    list_display = ('name', 'start_date', 'end_date')
    ordering = ('start_date',)

    search_fields = ['title', 'production_company__name', 'play__title']


class ProductionCompanyAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    actions_on_bottom = True
    save_on_top = True

    list_display = ('name',)
    search_fields = ['name', 'company_site']


class ProductionAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    actions_on_bottom = True
    save_on_top = True

    list_display = ('play__title', 'production_company__name',
        'start_date', 'end_date')
    list_filter = ('play__title', 'production_company__name', 'venue__name')
    ordering = ('start_date',)

    search_fields = ['play__title', 'production_company__name', 'venue__name']


class PlayAdmin(admin.ModelAdmin):
    actions_on_bottom = True
    save_on_top = True

    list_display = ('title', 'playwright')
    search_fields = ['title', 'playwright']


class VenueAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    actions_on_bottom = True
    save_on_top = True

    list_display = ('name', 'address__line_1', 'address__city')
    list_filter = ('address__city',)

    search_fields = ['name', 'address__line_1', 'address__city']


class ArtsNewsAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    actions_on_bottom = True
    save_on_top = True

    list_display = ('title', 'created_on')
    ordering = ('created_on',)

    search_fields = ['title', 'external_url']


class FestivalAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    actions_on_bottom = True
    save_on_top = True

    list_display = ('title', 'start_date', 'end_date')
    ordering = ('start_date',)

    search_fields = ['title', 'productions__play__title',
        'productions__production_company__name', 'plays__title',
        'production_companies__title', 'venues__name']


admin.site.register(Review, ReviewAdmin)
admin.site.register(Audition, AuditionAdmin)
admin.site.register(ProductionCompany, ProductionCompanyAdmin)
admin.site.register(Production, ProductionAdmin)
admin.site.register(Play, PlayAdmin)
admin.site.register(Venue, VenueAdmin)
admin.site.register(ArtsNews, ArtsNewsAdmin)
admin.site.register(Festival, FestivalAdmin)
