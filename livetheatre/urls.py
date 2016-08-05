from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from filebrowser.sites import site

from livetheatre import settings

urlpatterns = [
    url(r'^admin/filebrowser/', include(site.urls)),
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^bossman/', include(admin.site.urls)),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^search/', include('haystack.urls')),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^', include('base.urls')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
