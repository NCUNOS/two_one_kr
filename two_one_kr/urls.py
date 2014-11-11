from django.conf.urls import patterns, include, url

from django.contrib import admin

from spider import views
from squirrel import views
from deer import views

#autodiscovery();
#from mangonaut import *

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'two_one_kr.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', views.runDepListView.as_view(), name='temporaryHome'),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^spider/', include('spider.urls', namespace="spider")),
    url(r'^squirrel/', include('squirrel.urls', namespace="squirrel")),
    url(r'^deer/', include('deer.urls', namespace="deer")),
    url(r'^man/', include('man.urls', namespace="man")),
)
