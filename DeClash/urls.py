from django.conf.urls import patterns, include, url
from django.conf import settings

import autocomplete_light
autocomplete_light.autodiscover()

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'DeClash.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('rocketscience.urls')),
    url(r'^autocomplete/', include('autocomplete_light.urls')),
    #static
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.STATIC_ROOT}),
    #media
    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    #index
    url(r'^$', 'DeClash.views.home', name="home"),
)
