from django.conf.urls import patterns, url
from squirrel import views

urlpatterns = patterns('',
	# ex. /squirrel/init
	url(r'^init/$', views.InitView.as_view(), name='init'),
	url(r'^login/$', views.LoginView.as_view(), name='login'),
	url(r'^logout/$', views.LogoutView.as_view(), name='logout')
)