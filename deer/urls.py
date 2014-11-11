from django.conf.urls import patterns, url
from deer import views

urlpatterns = patterns('',
	# ex. /squirrel/init
	url(r'^run/dep/$', views.runDepListView.as_view(), name='runDep'),
	url(r'^run/dep/(?P<category>\w+)/$', views.runDepTreeListView.as_view(), name='runDepTree'),
	url(r'^run/course/(?P<pk>\w+)/(?P<url_encoding>[\w|\W]+)/$', views.runCourseDetailView.as_view(), name='runCourse'),
	#
	url(r'^bark/comment/(?P<course_tree>\w+)/$', views.barkCommentView.as_view(), name='barkComment'),
	url(r'^bark/msg/(?P<comment_id>\w+)/$', views.barkMsgView.as_view(), name='barkMsg'),
	#
	url(r'^stare/course/(?P<pk>\w+)/(?P<url_encoding>[\w|\W]+)/$', views.stareCourseView.as_view(), name='stareCourse'),

)