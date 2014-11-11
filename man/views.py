from __future__ import division

from django.shortcuts import render
from django.views.generic import View
from django.conf.urls import url
from django.http import HttpResponse

from spider.models import *

import mlpy
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg

# Create your views here.
class DotMapView(View):
	template_name = 'man/dotmap.html'
	def get(self, request, *args, **kwargs):
		return render(request, self.template_name, {'dep_id': self.kwargs['dep_id']})

class KMeansView(View):
	def get(self, request, *args, **kwargs):
		c = list()
		w = list()
		s = list()
		Xs = list()
		Ys = list()
		Zs = list()
		ce_list = CourseEssence.objects(category=self.kwargs['dep_id'])
		for ce in ce_list:
			try:
				c.index(ce.id)
			except:
				c.append(ce.id)
			s.append(0)
			x=c.index(ce.id)
			for pl in ce.tag_en_list:
				try:
					w.index(pl.word)
				except:
					w.append(pl.word)
				s[x]+=pl.freq


		np.random.shuffle(w)
		np.random.shuffle(c)

		arr = np.zeros((len(c),len(w))) #init a 2D array with x,y length
		for ce in ce_list:
			x = c.index(ce.id)
			for pl in ce.tag_en_list:
				y = w.index(pl.word)
				#arr[x][y] = pl.freq/s[x]
				Xs.append(x)
				Ys.append(y)
				Zs.append(pl.freq/s[x]*1000)
				arr[x][y] = pl.freq/s[x]


		#Xs, Ys = zip(*arr)
		arr  *= 1.0/arr.max() 
		Zs = np.array(Zs)
		Zs *= 1.0/Zs.max()

		cls, means, steps = mlpy.kmeans(arr, k=3, plus=True)
		fig = plt.figure(1)
		plot1 = plt.scatter(Xs, Ys, s=Zs, alpha=0.75)
		plot2 = plt.scatter(means[:,0], means[:,1], c=np.unique(cls), s=128, marker='d') # plot the means
		canvas = FigureCanvasAgg(fig)
		response = HttpResponse(content_type='image/png')
		canvas.print_png(response)
		return response

