# coding=UTF8
import requests
from pyquery import PyQuery as pq
from models import *
import slugify
import urllib
import json
import unirest
from microsofttranslator import Translator
import re
#import urllib2

class crawler():
	def crawlCourse(req_url, page=1):
		url = 'https://course.ncu.edu.tw/Course/main/query/byUnion?dept='+req_url+'&d-49489-p='+str(page)
		#dom = pq(url='https://course.ncu.edu.tw/Course/main/lang')
		dom = pq(url=url, headers={'Cookie': 'JSESSIONID=2ADBB7747EADBCFAF7A0E435B94B0B5F', 'Accept-Language': 'zh-tw,zh;q=0.8,en-us;q=0.5,en;q=0.3', 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:31.0) Gecko/20100101 Firefox/31.0'})
		#return dom
		#dom = dom.createDom()
		dep = dom.find('h5').text().split(u'搜尋結果  -- ')[1]
		#ex: https://course.ncu.edu.tw/Course/main/query/byUnion?dept=deptI1I2001I0
		dep_id = url.split('dept=')[1].split('I')[2]
		tr = dom.find('tbody')
		course_list = []
		#output = ''
		for i in tr.items('tr'):
			
			c = Course()
			c.serial_no = i('td').eq(0).text().split(' ')[0]
			c.reg_no = i('td').eq(0).text().split(' ')[1]
			c.ch_name = i('td').eq(1).text().split(' ')[0]
			c.en_name = i('td').eq(1).find('.engclass').text()
			
			#remarks and other opts
			desc = i('td').eq(1).find('.descript').text()
			#output += desc + '</br>'
			c.pwd_card = 0
			c.pwd_card = 1 if (u'部份使用' in desc) else c.pwd_card
			c.pwd_card = 2 if (u'全部使用' in desc) else c.pwd_card

			c.preselected = True if (u'[預選]' in desc) else False
			c.second_select = False if (u'[不開放初選]' in desc) else True
			c.language = desc.split(u'授課語言:')[1].split(']')[0] if (u'授課語言:' in desc) else '中文'
			c.graduate_institue = True if (u'碩博同修' in desc) else False
			c.remark = i('td').eq(1).filter('.notice').text() if i('td').eq(1).hasClass('notice') else ''
			c.teachers = i('td').eq(2).text().split(' ')
			c.credit = i('td').eq(3).text()

			#classtime seperation
			classtime = i('td').eq(4).text()
			for j in classtime.split(' '):
				p = Period()
				p.weekday = j[0:1]
				p.classroom = j.split('/')[-1]
				periods = j[1:].split('/')[0]
				k = 0
				while(k<len(periods)):
					p.periods.append(periods[k:k+1])
					k+=1
				c.period.append(p)

			c.required = True if i('td').eq(5).text() == u'必修' else False
			c.half = True if i('td').eq(6).text() == u'半' else False
			c.limited_ppl = 0 if i('td').eq(7).text() == u'無' else i('td').eq(7).text()
			c.semester = '1031'
			c.category = Category(_id = dep_id)
			c._id = 'NCU' + c.semester + c.serial_no

			course_list.append(c)

		while(len(course_list)%50 == 0):
			page+=1
			course_list.extend(crawlCourse(req_url, page))

		#output = course_list
		#return output
		return course_list

	def plantCourseTree(course_list):
		tree_list = []
		for c in course_list:
			#url: [NCU][MA2A][001]/[en_name]
			t = CourseTree()
			t._id = c._id[0:3] + c.reg_no[0:3] + c.reg_no.replace('*', '0')[len(c.reg_no)-1:] + c._id[len(c._id)-3:]
			t.en_url = slugify.slugify(unicode(c.en_name))
			t.ch_url = unicode(c.ch_name)
			l = CourseLeaf(semester = c.semester, course = c)
			t.course_leaves.append(l)
			t.pilot_course = c
			t.category = c.category
			tree_list.append(t)

			c.leaf_of = t

		return tree_list

	def createCategory():
		url = "https://course.ncu.edu.tw/Course/main/query/byUnion?dept=deptI0I1I1"
		dom = pq(url=url, headers={'Cookie': 'JSESSIONID=2ADBB7747EADBCFAF7A0E435B94B0B5F', 'Accept-Language': 'zh-tw,zh;q=0.8,en-us;q=0.5,en;q=0.3', 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:31.0) Gecko/20100101 Firefox/31.0'})
		faculties = dom.find('#byUnion_table')

		category_list = []
		for f in faculties.items('table'):
			faculty = f('th').eq(0).text().split('(')[0].replace(" ", "")
			for d in f.items('li'):
				cate = Category()
				cate._id = d.find('a').eq(0).attr('href').split('I')[2]
				cate.faculty = faculty
				cate.num = d.find('a').eq(0).text().split('(')[-1].split(')')[0]
				cate.dep = d.find('a').eq(0).text().replace('('+cate.num+')', '')
				cate.req_url = d.find('a').eq(0).attr('href').split('?dept=')[-1]
				category_list.append(cate)


		return category_list

	def translateText(textArray, fromLang, toLang):
		args = {
	        'client_id': '21KRtranslator',#your client id here
	        'client_secret': '1VYijs8FLyy7wmD/x1KsSWficJPiH61jywgGBM5m+iA=',#your azure secret here
	        'scope': 'http://api.microsofttranslator.com',
	        'grant_type': 'client_credentials'
	    }
		oauth_url = 'https://datamarket.accesscontrol.windows.net/v2/OAuth2-13'
		oauth_junk = json.loads(requests.post(oauth_url,data=urllib.urlencode(args)).content)
		translation_args = {
		        'text': textArr,
		        'to': toLang,
		        'from': fromLang
		        }
		headers={'Authorization': 'Bearer '+oauth_junk['access_token']}
		translation_url = ' http://api.microsofttranslator.com/V2/Http.svc/TranslationArray?'
		translation_result = requests.get(translation_url+urllib.urlencode(translation_args),headers=headers)
		return translation_result.content

	def crawlCourseEssence(course_list):
		url = "https://course.ncu.edu.tw/Course/main/query/byKeywords?"
		#ex: https://course.ncu.edu.tw/Course/main/query/byKeywords?serialNo=11001&outline=11001&semester=1031
		course_essence_list = []
		de = DepEssence()
		objective_buffer = []
		ob = 0
		content_buffer = []
		content_ch_buffer = []
		cb = 0
		translator = Translator('21KRtranslator', '1VYijs8FLyy7wmD/x1KsSWficJPiH61jywgGBM5m+iA=')
		for i, c in enumerate(course_list):
			if (i==0):
				de.id = str(c.category.id)
				de.category = c.category
				de.course_tree = c.leaf_of
				course_essence_list = []
			params = urllib.urlencode({'serialNo': c.serial_no, 'outline': c.serial_no, 'semester': c.semester})
			#dom = requests.get(url=url, params=params, headers={'Cookie': 'JSESSIONID=7257F09EDF368A37341694B4A4D7B72E', 'Accept-Language': 'zh-tw,zh;q=0.8,en-us;q=0.5,en;q=0.3', 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:31.0) Gecko/20100101 Firefox/31.0'})
			dom = pq(url=url+params, headers={'Cookie': 'JSESSIONID=7257F09EDF368A37341694B4A4D7B72E', 'Accept-Language': 'zh-tw,zh;q=0.8,en-us;q=0.5,en;q=0.3', 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:31.0) Gecko/20100101 Firefox/31.0'})
			raw = dom('script').text().encode('utf_8').decode('unicode_escape').split('\';')[0].replace('var JData = \'', '')
			data = json.loads(raw)
			try:
				if(data['msg']==u'notfound'):continue
			except KeyError:
				ce = CourseEssence()
				ce.id = c.id
				ce.course = c
				ce.course_tree = c.leaf_of
				ce.category = c.category
				ce.objective = unicode(data['courseObject']).replace('&nbsp;', ' ')
				ce.content = unicode(data['courseContent']).replace('&nbsp;', ' ')
				objective_buffer.append(ce.objective)
				content_buffer.append(ce.content)
				#return translator.translate_array(content_buffer, 'zh-CHT')
				ce.ability_list = []
				
				for m in data['courseMap']:
					if(m['strength']==u'N/A'):continue
					ability = CoreAbility(ability=unicode(m['core']), rating=m['strength'][1:2], evaluation=unicode(m['testType'])[0:-1].split(','))
					ce.ability_list.append(ability)

				course_essence_list.append(ce)
			
		
		i=0
		p = re.compile(ur'(\(\d*/\d*\))|(\d+\.)|(\d)|(<br/>)|(\([a-z]+\-[a-z]+\))|(\([a-z]+\-[a-z]+\s[a-z]+\))|()|(•)|(gt)|(^lt)|(\d*/\d*)|(败)|(^I{1,3})')
		while(i<=len(content_buffer)):
			min = 4 if (len(content_buffer)-i >= 4) else len(content_buffer)-i
			tmp_cont = translator.translate_array(content_buffer[i:i+min], 'en')
			#tmp_obj = translator.translate_array(objective_buffer[i:i+min], 'en')
			j=0
			for ce in course_essence_list[i:i+min]:
				ce.content_en = p.sub('', tmp_cont[j]['TranslatedText'])
				#ce.objective_en = tmp_obj[j]['TranslatedText']
				#ce.save()
				j+=1
			i+=5

		i=0
		while(i<=len(objective_buffer)):
			min = 4 if (len(objective_buffer)-i >= 4) else len(objective_buffer)-i
			#tmp_cont = translator.translate_array(content_buffer[i:i+min], 'en')
			tmp_obj = translator.translate_array(objective_buffer[i:i+min], 'en')
			j=0
			for ce in course_essence_list[i:i+min]:
				#ce.content_en = tmp_cont[j]['TranslatedText']
				ce.objective_en = p.sub('', tmp_obj[j]['TranslatedText'])
				ce.save()
				j+=1
			i+=5
		de.course_essence_list = course_essence_list
		de.save()
		return course_essence_list

	def createPhraseList(course_essence_list):
		outcome = []
		for ce in course_essence_list:
			response = unirest.post("https://textanalysis.p.mashape.com/textblob-noun-phrase-extraction",
				headers={"X-Mashape-Key": "GgF7BWbizBmshbUFGQfj5PSc4W8ip1AwraCjsn9QZVNEvPIO6f",  "Content-Type": "application/json"},
				params=json.dumps({"text": ce.objective_en+" "+ce.content_en}) )
			#response = requests.post(url="https://textanalysis.p.mashape.com/textblob-noun-phrase-extraction", headers={"X-Mashape-Key": "SacpytFgMjmshnlk7Jv5jfKAehCdp1T3XJHjsnkvUqUsDZ1Al1"}, params={"text": ce.objective_en+" "+ce.content_en})
			#response = response.json()
			#return json.dumps({"text": ce.objective_en+" "+ce.content_en})
			word_list = dict()
			phrase_en_list = []
			for n in response.body['noun_phrases']:
				try:
					word_list[n]+=1;
				except:
					word_list[n]=1;

			for w in word_list.items():
				phrase_en_list.append(Word(word=w[0], freq=w[1]))

			ce.phrase_en_list=phrase_en_list
			ce.save()
			outcome.append(phrase_en_list)
		return outcome

	def textseg(text):
		response = unirest.post("https://textanalysis.p.mashape.com/simple-text-summarizer",
			headers={"X-Mashape-Key": "GgF7BWbizBmshbUFGQfj5PSc4W8ip1AwraCjsn9QZVNEvPIO6f",  "Content-Type": "application/json"},
			params=json.dumps({"text": text}) )
		return response
