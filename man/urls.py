from django.conf.urls import patterns, url
from man import views

urlpatterns = patterns('',
	# ex: /man/dotmap/4009
	url(r'^dotmap/(?P<dep_id>\d+)/$', views.DotMapView.as_view(), name='dotmap'),
	url(r'^kmeans/(?P<dep_id>\d+)/$', views.KMeansView.as_view(), name='kmeans'),
)