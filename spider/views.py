# coding=UTF8
from __future__ import division

from django.shortcuts import render
from django.conf.urls import url
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import View, ListView, DetailView
from django.utils import simplejson

from mongoengine.django.shortcuts import get_document_or_404, get_list_or_404

from spider.models import *
import crawler
from sample import sample
import cal

from nltk.tokenize import word_tokenize
from nltk import FreqDist

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
		return HttpResponse(simplejson.dumps(data), mimetype="application/json")


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
		return HttpResponse(simplejson.dumps(data), mimetype="application/json")

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
		return HttpResponse(simplejson.dumps(data), mimetype="application/json")

class TestView(View):
	def get(self, request, *args, **kwargs):
		data=list()
		data.append(sample(seq=1, n=102, text="This is the third paper in a four companion paper sequence. In these papers, a hybrid parameter multiple body system (HPMBS) methodology is utilized to model the frictional contact/impact of aloose bolted joint between two sections of a cantilever beam undergoing planar slewing motion. In this preliminary model, a \u001crigid\u001d joint is utilized, allowing the members of the joint to berigid, each attached to an elastic beam section. Frictional contact/impact is modeled at four contact points. The contact constraints and momentum transfer are modeled with the idea of instantly applied nonholonomic constraints. In this paper, the contact and switching algorithms, the numerical solution scheme, and simulation results are presented. The theoretical model of the variable structure dynamic system, the momentum transfer equations and the experimental comparison are presented elsewhere. The motivation for this work is the need for accurate low order models of complicated nonlinear phenomena in structural systems."))
		data.append(sample(seq=2, n=123, text="This article is the last of a set of four companion articles. In these articles, a hybrid parameter multiple body system (HPMBS) methodology is utilized to model the frictional contact/impact of a loose bolted joint between two sections of a cantilever beam undergoing planar slewing motion. In this preliminary model, a \u001crigid\u001d joint is utilized, which allows the members of the joint to be rigid, each attached to the elastic beam sections. Frictional contact/impact is modeled at four contact points. The contact constraints and momentum transfer are modeled with the idea of instantly applied nonholonomic constraints. This article addresses the experimental justification for the model, and our experimental apparatus is described herein. Simulation results and experimental results for the rigid joint configuration are compared and discussed. The theoretical model, the momentum transfer equations utilizing the concept of instantly applied nonholonomic constraints, and the numerical solution scheme are presented in the three companion articles. The motivation for this work is the need for low order but nonetheless accurate models of complicated nonlinear phenomena in structural systems."))
		data.append(sample(seq=3, n=47, text="In this paper the dynamics of a non-linear system with non-ideal excitation are studied. An unbalanced motor with a strong non-linear structure is considered. The excitation is of non-ideal type. The model is described with a system of two coupled strong non-linear differential equations. The steady state motions and their stability is studied applying the asymptotic methods. The existence of the Sommerfeld effect in such non-linear non-idealy excited system is proved. For certain values of system parameters chaotic motion appears. The chaos is realized through period doubling bifurcation. The results of numerical simulation are plotted and the Lyapunov exponents are calculated. The Pyragas method for control of chaotic motion is applied. The parameter values for transforming the chaos into periodical motion are obtained."))
		data.append(sample(seq=4, n=149, text="In this paper a non-ideal mechanical system with clearance is considered. The mechanical model of the system is an oscillator connected with an unbalanced motor. Due to the existence of clearance the connecting force between motor and the fixed part of the system is discontinuous but linear. The mathematical model of the system is represented by two coupled second-order differential equations. The transient and steady-state motion and also the stability of the system are analyzed. The Sommerfeld effect is detected. For certain values of the system parameters the motion is chaotic. This is caused by the period doubling bifurcation. The existence of chaos is proved with maximal Lyapunov exponent. A new chaos control method based on the known energy analysis is introduced and the chaotic motion is transformed into a periodic one."))
		data.append(sample(seq=5, n=446, text="The most important problem related to internal wave observation is that it is difficult to obtain clear results with in-situ observations. There are many factors, including the topography, time, season, wind and temperature, which may affect the shape of the wave, perhaps even making it disappear or not leave strong evidence. This paper discusses the research on in-situ observations of such waves in oceans, estuaries and lakes. Over the past decades, researchers have observed this phenomenon and have carried out numerical experiments about these internal solitary waves. They have used high tech equipment and mathematical methods to detect and calculate the results of wave vibration and simulate the in-situ conditions seen during wave turbulence. We focus on the in-situ observation of such waves in oceans, estuaries and lakes, surveying scholarly work over the past few years from a wide variety of places including Europe, the United States, South Africa, Taiwan, the South China Sea and the Yellow Sea. Even now, with the rapid development of new technology for use in in-situ observations, there are still many elements of the behavior of such waves that remain to be solved."))
		data.append(sample(seq=6, n=704, text="Although neural networks (NNs) have been successfully applied many times, there are still some drawbacks in any control scheme. In this study an NN-based model is applied for an n-degree ecosystem. The Takagi-Sugeno fuzzy model representation and fuzzy Lyapunov method are extended to analyze the ecosystem stability. During the stability analysis, the linear matrix inequality conditions are derived using the fuzzy Lyapunov theory to guarantee the stability and stabilization of the n-degree ecosystems. The suitability of the proposed stability conditions are demonstrated with a numerical simulation."))
		data.append(sample(seq=7, n=443, text="This paper describes how risk-based risk control allocation models work on pressure vessels and piping. We begin by discussing the economic rationale for allocating risk control in a diversified organization such as an enterprise. Considering a probability model for risk control decision making under uncertainty and risk, we propose a model involving stochastic total-loss amount constraints with respect to various tolerable default levels. Our main objective is to develop a method that would allow shaping the risk associated with risk control outcomes. The direct and indirect losses caused by the simulated disasters can be estimated using the engineering and financial analysis model. Based on this model, we can generate an exceeding probability (EP) curve and then calculate how much loss will be eliminated or transferred to other entities should funds be allocated to risk control. Optimal natural disaster risk control arrangement with probabilistic formulation is explained in this paper. Results from the proposed formulations are compared in case studies. The model attempts to apply risk based budget guidelines to risk reduction measurement within a portfoliobased risk framework"))
		data.append(sample(seq=8, n=484, text="Although there have been numerous studies about the mechanical control of autonomous humanoid robots and the human-robot interaction, there has been little discussion of the whole system within a local area required to manage many robots. Reports on the deployment or placing of robots in local areas have revealed more about what comprise effective and low-cost humanoid robots without taking into consideration the weight and size of objects. Current recognition systems for human- robot interaction should allow for quick behavioral decisions and the feedback for different objects is important. This study proposes a review model that will provide satisfactory optimal mechanical control anywhere and be expandable to any type of area. However, the natural environment is extremely complex and there are many factors that will affect the behavior of robots. We divide and conquer the problem by solving small problems in the whole system. In recent studies some categories have been evaluated to help determine where the main attention should be directed. In this review study we look at how to construct the proposed system within a local area then expand it to a wider area."))
		data.append(sample(seq=9, n=231, text="Based on adaptive inverse control theory, combined with neural network, neural network adaptive inverse controller is developed and applied to an electro-hydraulic servo system. The system inverse model identifier is constructed by neural network. The task is accomplished by generating a tracking error between the input command signal and the system response. The weights of the neural network are updated by the error signal in such a way that the error is minimized in the sense of mean square using (LMS) algorithm and the neural network is close to the system inverse model. The above steps make the gain of the serial connection system close to unity, realizing waveform replication function in real-time. To enhance its convergence and robustness, the normalized LMS algorithm is applied. Simulation in which nonlinear dead-zone is considered and experimental results demonstrate that the proposed control scheme is capable of tracking desired signals with high accuracy and it has good real-time performance."))
		data.append(sample(seq=10, n=498, text="In this paper, we study dynamic isotropy using natural frequency analysis for a class of symmetric spatial parallel mechanisms (SSPMs) with 2p (pe3) struts. This kind of dynamic isotropy has been defined as the square roots of the eigenvalues of the equivalent mass-spring systems formed via the interactions between rigid-body mechanical systems and their driving systems. Analytic expressions for these eigenvalues are then derived in the task space, which is linearly dependent on p. Furthermore, a general compliance center was found for all the SSPMs in which the parallel mechanisms are fully decoupled. Based on the dynamically decoupling, then, dynamic isotropy for the SSPM is discussed which shows that though taking the inertial parameters into consideration, the SSPM can not attain complete dynamic isotropy and the optimal dynamic isotropy index is the quartic root of two. At the end of the paper, to demonstrate these results, an example is given."))
		data.append(sample(seq=11, n=60, text="The objective of this research is to investigate the feasibility of utilizing eigenvector assignment and piezoelectric circuitry for enhancing vibration isolation performance of periodic isolators. For a classical periodic structure, stop bands are created due to material discontinuity so that wave propagation of external excitation can be suppressed within the stop band frequency range. While effective, such a method cannot always create wide enough stop bands such that all disturbance frequencies are covered. In this study, the eigenvector assignment technique and piezoelectric circuitry are utilized to reduce the transmissibility of the isolator modes near the boundary of the stop bands, and therefore widen the effective frequency range of vibration suppression of the periodic isolator. The principle of eigenvector assignment is to alter the mode shapes of the system so that the modal components corresponding to the concerned coordinates are as small as possible. By applying the eigenvector assignment method on the spatially tailored periodic isolator structure, the response amplitude of the attenuated end (the end of the isolator designed to have small vibration) at resonant frequencies near the stop band can be reduced, which enhances the vibration isolation performance in the frequency range of interest. On the other hand, piezoelectric circuits"))
		data.append(sample(seq=12, n=66, text="Largely due to their self-aligning and superior loading capabilities, spherical roller bearings have seen extensive application. Compared with the single-row deep-grooved-ball (DGB) bearing, the dynamics involved in the operation of double-row spherical roller bearings (SRBs) are much more complicated; double-row SRBs have at least twice as many degrees of freedom (DoFs) as DGBs. Also, the contact forces between each one of a pair of rollers and the inner race/outer race can be different, resulting in unbalanced axial forces on the moving race and causing axial displacement and angular movements of the moving race. Due to its complexity, modeling efforts carried out so far have not included the effects of the rotational DoFs of the moving race. Aiming at improving the state of the art, a comprehensive dynamic model of SRBs is developed in this investigation. This model takes into account all the DoFs of the moving race, including the angular movements about both the vertical and horizontal axes. Subsequently, the contact angle between each individual roller and the moving race is correlated with each linear and rotational DoF of the moving race. The model developed in this investigation can quantitatively analyze the effects of linear and rotational shaft misalignments. Therefore, it provides guidelines for optimizing system installation"))
		data.append(sample(seq=13, n=361, text="In this paper, an improved feed-forward inverse control scheme is proposed for transient waveform replication (TWR) on an electro-hydraulic shaking table (EHST). TWR is to determine whether a test article can remain operational and retain its structural integrity when subjected to a specific shock and vibration environment. Feed-forward inverse transfer function compensation is a useful technique to improve the tracking accuracy of the TWR on the EHST system due to their inherent hydraulic dynamics. Whenever a feed-forward inverse transfer function is employed, it is critical to design the identification accuracy of the inverse transfer function. A combined control strategy, which combines a feed-forward inverse transfer function compensation approach with a simple internal model control (IMC) and a real-time feedback controller, is proposed to minimize the effect of the system uncertainty and modeling error, and further to improve the tracking accuracy of the TWR. Thus, the proposed control strategy combines the merits of feed-forward inverse transfer function compensation and IMC. The procedure of the proposed control strategy is programmed in MATLAB/Simulink, and then is compiled to a real-time PC with Microsoft Visual Studio.NET for implementation. Simulation and experimental results demonstrated the viability of the proposed"))
		data.append(sample(seq=14, n=463,text="The acceleration output of an electro-hydraulic servo system corresponding to a sinusoidal input contains higher harmonics besides the fundamental input, because of complex nonlinearities occurring in the system. This causes harmonic distortion of the acceleration signal. The method for harmonic elimination based on adaptive notch filter is proposed here. The task is accomplished by generating a reference signal with a frequency that should be eliminated from the output. The reference input is filtered in such a way that it closely matches the harmonic. The filtered reference signal is added to the fundamental signal such that the output harmonic is cancelled leaving the desired signal alone. The weights of the adaptive filter are adjusted by the error between the input and the feedback acceleration to eliminate acceleration harmonic, creating an adaptive notch filter. The above concept is used as a basis for the development of an acceleration harmonic cancellation algorithm. Results of simulation and experiment on an electro-hydraulic servo shaking table demonstrate the efficiency and validity of the proposed control scheme."))
		data.append(sample(seq=15, n=419, text="In order to improve the low-frequency acoustic performance, a composite sound absorption coating made by embedding another viscoelastic material into the viscoelastic substrate of the traditional sound absorption coating, has been developed. Compared to the substrate, the transverse wave speed of the embedded-layer is lower. Accounting for the symmetry, the unit cell of the traditional sound absorption coating or the composite sound absorption coating could be approximately regarded as a viscoelastic single-layer cylindrical tube or a viscoelastic double-layer cylindrical tube, respectively. The plane wave normally impinging on the sound absorption coating only excites the axisymmetric wave propagating in the axial direction of the viscoelastic cylindrical tube. If the complex axisymmetric wave number and the effective impedance of the viscoelastic cylindrical tube are obtained, the acoustic performance of the sound absorption coating could be evaluated by using the transfer matrix method, which is suitable for both the single-layer cylindrical tube and the double- layer cylindrical tube. Numerical results show that the peak frequency of the sound absorption coefficient is shifted to the lower location as the proportion of the embedded-layer increases, or the transverse wave speed of the embedded-layer decreases.	"))
		data.append(sample(seq=16, n=669, text="The principle of equal modal damping is used to give a unified presentation and calibration of resonant control of structures for different control formats, based on velocity, acceleration\u0013position or position feedback. When introducing a resonant controller the original resonant mode splits into two, and if these are required to have the same modal damping ratio, the characteristic equation conforms to a two-parameter format. By selecting a suitable relative separation of the modal frequencies, the design problem defines a one-parameter family \u0013 determined, for example, in terms of the resulting modal damping ratio. While velocity feedback, and the associated acceleration\u0013position formats, lead to near-equal resonant peak heights of the velocity in a frequency response diagram, position feedback leads to balanced acceleration peaks. It is demonstrated, how a simple additional time derivative term in the control coupling can change these properties into balanced position and velocity peaks, respectively. In particular this gives an improved control format based on measurement of structural displacement or deformation. In all cases the optimal calibration in terms of a root locus identification leads to a simple explicit pair of design formulae for controller frequency and damping ratio based on a simple two -degrees-"))
		data.append(sample(seq=17, n=343, text="The design method of -synthesis controller for the flexible cable-strut structure with mixed uncertainties was presented and verified by the simulation experiments. The uncertainties include model uncertainties caused by joint clearance and friction, and the uncertainties arising from the actuator range and sensor noise. Based on the structured singular value theory, the model of robust active vibration control for the flexible cable-strut structure was established. The robust performance of the external disturbance rejection is characterized by introducing a fictitious uncertainty block across the disturbance/error channels and carrying out a robust stability analysis. The controller was derived from minimizing the structured singular value. This method considers the structural characteristics of the mixed uncertainty block, so that the conservativeness of H\u001e controller in dealing with the mixed uncertainty problem is avoided. The simulation results show that the method has good robustness and stability performances for the controlled system with mixed uncertainties and external disturbances."))
		data.append(sample(seq=18, n=462, text="Squeeze film damping effects naturally occur if structures are subjected to loading situations such that a very thin film of fluid is trapped within structural joints, interfaces, etc. An accurate estimate of squeeze film effects is important to predict the performance of dynamic structures. This paper presents a finite element solution to the coupled fluid\u0013structure problem of squeeze film dampers. The squeeze film is governed by the linearized isothermal Reynolds equation, which is known from lubrication theory. The structure which is modeled using Reissner\u0013Mindlin plate theory is discretized by four-noded two-dimensional shear deformable isoparametric plate elements. The coupled finite element formulation is derived and an alternative solution to obtain damped eigenvalues and eigenvectors is presented. The coupling between fluid and structure is handled by considering the pressure forces and structural surface velocities on the boundaries. The effects of the driving parameters on the frequency response functions are investigated. It was found that the ambient pressure has no significant effect on the frequency responses, unlike on the damping force of dynamical MEMS systems. The results obtained from the presented model are compared with the experimental and analytical results available in the literature and a very good agreement is found."))


		
		bigDict = dict()
		attr = dict()
		html="<h1>Word Frequency</h1><table><tr><th>index</th>"

		for key, d in enumerate(data):
			bigDict[d.n] = FreqDist(word_tokenize(d.text.lower()))
			attr = dict(attr.items() + bigDict[d.n].items())

		for a, b in attr.items():
			attr[a]=0

		for key, d in enumerate(data):
			bigDict[d.n]=dict(attr.items() + bigDict[d.n].items())



		#render
		for a in attr:
			html+="<td>"+a+"</td>"
		html+="</tr>"

		for key, d in enumerate(data):
			html+="<tr><th>"+str(d.n)+"</th>"
			for a, b in attr.items():
				html+="<td>"+str(bigDict[d.n][a])+"</td>"
			html+="</tr>"
		html+="</table><br/>"

		#eculidean distance
		distDict = cal.e_distDict(bigDict, data, attr)

		html+="<h1>Eculidean Distance</h1><table>"
		for key1, d1 in enumerate(data):
			html+="<tr><th>"+str(d1.n)+"</th>"
			for key2, d2 in enumerate(data):
				html+="<td>"+ str(distDict[d1.n][d2.n])+"</td>"
			html+="</tr>"
		html+="<tr><td>p1/p2</td>"
		for key2, d2 in enumerate(data):
			html+="<th>"+str(d2.n)+"</th>"
		html+="</tr></table>"

		result = cal.e_similarity(distDict)
		html+="similar: <br/>"
		for d in result['similar']:
			html+=str(d['p1'])+" <-> "+str(d['p2'])+"<br/>"
		html+="</br>dissimilar: "
		for d in result['dissimilar']:
			html+=str(d['p1'])+" <-> "+str(d['p2'])+"<br/>"




		return HttpResponse(html)



