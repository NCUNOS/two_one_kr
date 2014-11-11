from django.conf.urls import patterns, url
from spider import views

urlpatterns = patterns('',
	# ex: /spider/
	url(r'^$', views.IndexListView.as_view(), name='index'),
	# ex: /spider/search/[dep_id]/(page)
	url(r'^search/(?P<req_url>\w+)/$', views.SearchView.as_view(), name='search'),
	# ex: /spider/observe
	url(r'^observe/$', views.ObserveListView.as_view(), name='observe'),
	# ex: /spider/observe/[NCU][MA2A][001]/[en_name]||[ch_name]
	url(r'^observe/(?P<pk>\w+)/$', views.ObserveDetailView.as_view(), name='observeDetail'),
	# ex: /spider/create/index, init index
	url(r'^create/index/$', views.CreateIndexView.as_view(), name='createIndex'),
	url(r'^create/categoryfortree/$', views.CreateCateForTreeView.as_view(), name='createCateForTree'),
	url(r'^create/courseessence/(?P<dep_id>\d+)/$', views.CreateCourseEssenceView.as_view(), name='createCourseEssence'),
	url(r'^create/tag_list/$', views.CreateCourseTagListView.as_view(), name='createTagList'),
	url(r'^create/phrase_list/(?P<dep_id>\d+)/$', views.CreateCourseEssenceByPhraseView.as_view(), name='createPhraseList'),
	# ex: /spider/inspect/[semester]/[dep_id]
	url(r'^inspect/(?P<semester>\d+)/(?P<dep_id>\d+)/$', views.DepListView.as_view(), name='depList'),
	# ex: /spider/abilitychart/[dep_id]
	url(r'^abilitychart/(?P<dep_id>\d+)/$', views.AbilityChartView.as_view(), name='abilityChart'),
	url(r'^abilitychart/api/(?P<dep_id>\d+)/$', views.GetAbilityJSON.as_view(), name='abilityAPI'),
	url(r'^abilitybarchart/(?P<dep_id>\d+)/$', views.AbilityBarChartView.as_view(), name='abilityBarChart'),
	url(r'^abilitybarchart/api/(?P<dep_id>\d+)/$', views.GetAbilityBarJSON.as_view(), name='abilityBarAPI'),

	url(r'^dotmap/api/(?P<dep_id>\d+)/$', views.DotMapJSON.as_view(), name='dotMapAPI'),
	url(r'^test/$', views.TestView.as_view(), name='test'),
)