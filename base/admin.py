from django.contrib import admin

from base.models import *

class ReviewAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}

class ProductionCompanyAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

class ProductionAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}

class ArtsNewsAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}

class VenueAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Review, ReviewAdmin)
admin.site.register(Audition)
admin.site.register(ProductionCompany, ProductionCompanyAdmin)
admin.site.register(Production)
admin.site.register(Play)
admin.site.register(Venue, VenueAdmin)
admin.site.register(Address)
admin.site.register(ArtsNews, ArtsNewsAdmin)
admin.site.register(Festival)
