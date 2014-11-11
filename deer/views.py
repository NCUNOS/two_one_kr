from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import View, ListView, DetailView

from django.contrib.sessions.models import Session
from django.contrib.auth.models import User

from spider.models import *
from deer.models import *
from squirrel.models import *

# Create your views here.

class runDepListView(ListView):
	queryset = Category.objects.order_by('_id', 'faculty')
	template_name = 'deer/run_dep.html'
	context_object_name = 'category_list'

class runDepTreeListView(ListView):
	template_name = 'deer/run_dep_tree.html'
	context_object_name = 'tree_list'
	def get_queryset(self):
		self.tree_list = CourseTree.objects(category=self.kwargs['category'])
		return self.tree_list

	def get_context_data(self, **kwargs):
		context = super(runDepTreeListView, self).get_context_data(**kwargs)
		context['category'] = Category.objects.get(pk=self.kwargs['category'])
		return context

class runCourseDetailView(DetailView):
	template_name = 'deer/run_course.html'
	context_object_name = 'course_tree'
	def get_object(self):
		self.course_tree = CourseTree.objects(pk=self.kwargs['pk']).first()
		return self.course_tree
	def get_context_data(self, **kwargs):
		context = super(runCourseDetailView, self).get_context_data(**kwargs)
		context['comment_list']=Comment.objects(left_for=self.kwargs['pk'])
		return context

class barkCommentView(View):
	def post(self, request, *args, **kwargs):

		c = Comment(abstract=request.POST['abstract'], left_by=request.user.id, left_for=self.kwargs['course_tree'])
		c.save()
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
		
class barkMsgView(View):
	def post(self, request, *args, **kwargs):
		c = Comment.objects.get(id=self.kwargs['comment_id'])
		m = Msg(text=request.POST['text'], left_by=request.user.id)
		c.msgs.append(m)
		c.save()
		#return HttpResponse(c)
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

class stareCourseView(View):
	template_name = 'deer/stare_course.html'
	def get(self, request, *args, **kwargs):
		course_tree = CourseTree.objects.get(pk=self.kwargs['pk'])
		return render(request, self.template_name, {'course_tree': course_tree})
