from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin


from livetheatre import settings

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'livetheatre.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^$', include('base.urls')),
)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
