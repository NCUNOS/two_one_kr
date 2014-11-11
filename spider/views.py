# coding=UTF8
from __future__ import division

from django.shortcuts import render
from django.conf.urls import url
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import View, ListView, DetailView
import json

from mongoengine.django.shortcuts import get_document_or_404, get_list_or_404

from spider.models import *
from spider.crawler import crawler as crawler

class IndexListView(ListView):
	queryset = Category.objects.order_by('_id', 'faculty')
	template_name = 'spider/index.html'
	context_object_name = 'category_list'

class DepListView(ListView):
	template_name = 'spider/dep_list.html'
	context_object_name='course_list'
	def get_queryset(self):
		self.course_list = Course.objects(semester=self.kwargs['semester'], category=self.kwargs['dep_id'])
		return self.course_list

	def get_context_data(self, **kwargs):
		context = super(DepListView, self).get_context_data(**kwargs)
		context['category'] = Category.objects.get(pk=self.kwargs['dep_id'])
		context['semester'] = self.kwargs['semester']
		context['fetched_course_num'] = self.course_list.count()
		return context


class SearchView(View):
	def get(self, request, *args, **kwargs):
		course_list = crawler.crawlCourse(self.kwargs['req_url'])
		tree_list = crawler.plantCourseTree(course_list)
		for c in course_list:
			c.save()

		for t in tree_list:
			t.save()

		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

class ObserveListView(ListView):
    queryset = Course.objects.all
    context_object_name = 'course_list'
    template_name = 'spider/observe_list.html'


class ObserveDetailView(DetailView):
	model = CourseTree
	context_object_name = 'tree'
	template_name = 'spider/observe_detail.html'

	def get_object(self):
		tree = get_document_or_404(CourseTree, pk=self.kwargs['pk'])
		return tree

class CreateIndexView(View):
	def get(self, request, *args, **kwargs):
		category_list = crawler.createCategory()
		for cate in category_list:
			cate.save()

		return HttpResponse(category_list)

class CreateCateForTreeView(View):
	def get(self, request, *args, **kwargs):
		'''for t in CourseTree.objects:
			t.del('course_leaves')'''
		return HttpResponse('he')


class CreateCourseEssenceView(View):
	template_name = 'spider/create_courseessence.html'
	def get(self, request, *args, **kwargs):
		course_list = Course.objects(category=self.kwargs['dep_id'])
		#course_essence_list = crawler.crawlCourseEssence(course_list)
		#return HttpResponse(course_essence_list)
		course_essence_list = CourseEssence.objects(category=self.kwargs['dep_id'])

		return render(request, self.template_name, {'course_essence_list': course_essence_list, 'course_list': course_list})


class CreateCourseEssenceByPhraseView(View):
	def get(self, request, *args, **kwargs):
		course_essence_list = CourseEssence.objects(category=self.kwargs['dep_id'])
		phrase_list = crawler.createPhraseList(course_essence_list)
		return HttpResponse(phrase_list)


class CreateCourseTagListView(View):
	def post(self, request, *args, **kwargs):
		outcome=[]
		for i, ce in enumerate(request.POST.getlist('ce[]')):
			tag_en_list = []
			word_list = request.POST.getlist('word'+str(i)+'[]')
			freq_list = request.POST.getlist('freq'+str(i)+'[]')
			#return HttpResponse(word_list)
			for j, chkbox in enumerate(request.POST.getlist('chkbox'+str(i)+'[]')):
				#if(chkbox == u'off'):continue
				tag_en_list.append(Word(word=word_list[int(chkbox)], freq=freq_list[int(chkbox)]))
			CourseEssence.objects(pk=ce).update(set__tag_en_list=tag_en_list)
			outcome.append(word_list)
			#return HttpResponse(chkbox)
		return HttpResponse(outcome)



class GetAbilityJSON(View):
	def get(self, request, *args, **kwargs):
		course_essence_list = CourseEssence.objects(category=self.kwargs['dep_id'])
		data=dict()
		data['datasets']=[]
		data['labels']=[]
		for ce in course_essence_list:
			for ability in ce.ability_list:
				if ability.ability not in data['labels']:
					data['labels'].append(ability.ability)
		for ce in course_essence_list:
			ce_datasets=dict()
			ce_datasets['label'] = ce.course.ch_name
			ce_datasets['pointColor'] = 'rgba(242,64,66,1)' if ce.course.required == True else 'rgba(99,166,241,1)'
			ce_datasets['fillColor'] = 'rgba(242,64,66,0.2)' if ce.course.required == True else 'rgba(99,166,241,0.2)'
			ce_datasets['strokeColor'] = 'rgba(0, 0, 0, 0)'
			#ce_datasets['pointHighlightFill'] = "#fff"
			#ce_datasets['pointHighlightStroke'] = "rgba(220,220,220,1)" if ce.course.required == True else "rgba(151,187,205,1)"
			ce_datasets['data']=[0]*len(data['labels'])
			for d in ce.ability_list:
				ce_datasets['data'][data['labels'].index(d.ability)]=d.rating
			data['datasets'].append(ce_datasets)
		return HttpResponse(json.dumps(data), mimetype="application/json")


class AbilityChartView(View):
	template_name = 'spider/abilitychart.html'
	def get(self, request, *args, **kwargs):
		return render(request, self.template_name, {'dep_id': self.kwargs['dep_id']})

'''
var data = {
    labels: ["January", "February", "March", "April", "May", "June", "July"],
    datasets: [
        {
            label: "My First dataset",
            fillColor: "rgba(220,220,220,0.5)",
            strokeColor: "rgba(220,220,220,0.8)",
            highlightFill: "rgba(220,220,220,0.75)",
            highlightStroke: "rgba(220,220,220,1)",
            data: [65, 59, 80, 81, 56, 55, 40]
        },
        {
            label: "My Second dataset",
            fillColor: "rgba(151,187,205,0.5)",
            strokeColor: "rgba(151,187,205,0.8)",
            highlightFill: "rgba(151,187,205,0.75)",
            highlightStroke: "rgba(151,187,205,1)",
            data: [28, 48, 40, 19, 86, 27, 90]
        }
    ]
};
'''

class GetAbilityBarJSON(View):
	def get(self, request, *args, **kwargs):
		course_essence_list = CourseEssence.objects(category=self.kwargs['dep_id'])
		data=dict()
		data['datasets']=[]
		data['labels']=[]
		for ce in course_essence_list:
			for ability in ce.ability_list:
				if ability.ability not in data['labels']:
					data['labels'].append(ability.ability)

		counts = [[0 for x in xrange(len(data['labels']))] for x in xrange(2)] 
		nums = [[0 for x in xrange(len(data['labels']))] for x in xrange(2)] 
		for ce in course_essence_list:
			r = 1 if ce.course.required==True else 0
			for ability in ce.ability_list:
				counts[r][data['labels'].index(ability.ability)]+=ability.rating
				nums[r][data['labels'].index(ability.ability)]+=1

		for r in range(0, 2):
			d=dict()
			d['label']= u'必修' if r==1 else u'選修'
			d['pointColor'] = 'rgba(242,64,66,1)' if r == 1 else 'rgba(99,166,241,1)'
			d['fillColor'] = 'rgba(242,64,66,0.2)' if r == 1 else 'rgba(99,166,241,0.2)'
			d['strokeColor'] = 'rgba(0, 0, 0, 0)'
			d['data']=[]
			for i in range(0, len(data['labels'])):
				d['data'].append(round(counts[r][i]/nums[r][i], 2))
			data['datasets'].append(d)
		return HttpResponse(json.dumps(data), mimetype="application/json")

class AbilityBarChartView(View):
	template_name = 'spider/abilitybarchart.html'
	def get(self, request, *args, **kwargs):
		return render(request, self.template_name, {'dep_id': self.kwargs['dep_id']})

class DotMapJSON(View):
	def get(self, request, *args, **kwargs):
		nodes=[]
		links=[]
		tags=[]
		course_essence_list = CourseEssence.objects(category=self.kwargs['dep_id'])
		for ce in course_essence_list:
			n=dict()
			n['name'] = ce.course.ch_name
			n['artist'] = ce.course.en_name
			n['id'] = u'c'+ce.course.en_name
			n['playcount'] = int(ce.course.credit)*10
			nodes.append(n)
			for tag in ce.phrase_en_list:
				try:
					x=tags.index(tag.word)
					nodes[x]['artist']+=int(tag.freq)
					nodes[x]['playcount']+=int(tag.freq)
				except:
					tags.append(tag.word)
					n=dict()
					n['name']=tag.word
					n['artist']=int(tag.freq)
					n['id'] = u't'+tag.word
					n['playcount'] = int(tag.freq)
					nodes.append(n)
				l=dict()
				l['source']=u'c'+ce.course.en_name
				l['target']=u't'+tag.word
				links.append(l)
		data=dict()
		data['nodes']=nodes
		data['links']=links
		return HttpResponse(json.dumps(data), mimetype="application/json")

