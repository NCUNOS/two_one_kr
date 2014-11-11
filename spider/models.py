# coding=UTF8
from mongoengine import *
import urllib
# Create your models here.

from deer.models import *

# Course

class Period(EmbeddedDocument):
	weekday = StringField(help_text='星期')
	periods = ListField(StringField(help_text='課數'))
	classroom = StringField(help_text='教室')

class Course(Document):
	_id = StringField(required=True, help_text='21kr流水號', primary_key=True)
	serial_no = StringField(required=True, help_text='流水號')
	reg_no = StringField(help_text='課號')
	ch_name = StringField(help_text='中文課名')
	en_name = StringField(help_text='英文課名')
	teachers = ListField(StringField(help_text='授課老師'))
	credit = IntField(help_text='學分數')
	period = ListField(EmbeddedDocumentField(Period),help_text='授課時間')
	required = BooleanField(help_text='true = 必修；false = 選修')
	half = BooleanField(help_text='true = 一學期；false = 全學年')
	limited_ppl = IntField(default=0, help_text='人數上限')
	semester = IntField(help_text='學期')
	category = ReferenceField('Category',help_text='分類')
	remark = StringField(help_text='備註')
	pwd_card = IntField(default=0, help_text='0 = 不使用；1 = 部分使用；2 = 全部使用')
	language = StringField(default='中文', help_text='預設為中文')
	preselected = BooleanField(default=False, help_text='true = 預選；false = 非預選')
	second_select = BooleanField(default=False, help_text='true = 不開放初選')
	graduate_institute = BooleanField(default=False, help_text='true = 碩博同修；false = 一般')
	leaf_of = ReferenceField('CourseTree')
	def __unicode__(self):
		return '[#%s] %s (%s) , %s <br/>' % (self.serial_no, self.ch_name, self.en_name, self.teachers)
	def getURL(self):
		return self.leaf_of + '/' + urllib.quote(unicode(self.ch_name).encode('utf8')) + '/'
	meta = {'allow_inheritance': True, 'indexes':['serial_no']}

class GeneralCourse(Course):
	core = BooleanField(help_text='true = 核心通識；false = 選修通識')
	domain = StringField(help_text='領域')

#CourseEssence

class Word(EmbeddedDocument):
	word = StringField()
	freq = IntField()

class CoreAbility(EmbeddedDocument):
	ability = StringField()
	rating = IntField()
	evaluation = ListField(StringField())
	meta = {'indexes':['ability']}

class CourseEssence(Document):
	_id = StringField(required=True, primary_key=True)
	course = ReferenceField(Course, required=True)
	course_tree = ReferenceField('CourseTree', required=True)
	category = ReferenceField('Category')
	objective = StringField()
	objective_ch = StringField()
	objective_en = StringField()
	content = StringField()
	content_ch = StringField()
	content_en = StringField()
	tag_en_list = ListField(EmbeddedDocumentField(Word))
	phrase_en_list = ListField(EmbeddedDocumentField(Word))
	ability_list = ListField(EmbeddedDocumentField(CoreAbility))
	def __unicode__(self):
		return '[#%s] %s <br/> %s <br/>' % (self.pk, self.content, self.objective)

	meta = {
        'ordering': ['_id']
    }

#DepEssence

class DepEssence(Document):
	_id = StringField(required=True, primary_key=True)
	category = ReferenceField('Category', required=True)
	objective_list = ListField(EmbeddedDocumentField(Word))
	content_list = ListField(EmbeddedDocumentField(Word))
	course_essence_list = ListField(ReferenceField(CourseEssence))


#Category

class Category(Document):
	_id = IntField(help_text='系所代碼', required=True, primary_key=True)
	faculty = StringField(help_text='學院/中心/處室')
	dep = StringField(help_text='系所')
	num = IntField(help_text='開課數')
	req_url = StringField()
	def __unicode__(self):
		return '[#%s] %s / %s (%s) <br/>' % (self.pk, self.faculty, self.dep, self.num)
	meta = {
        'ordering': ['_id', 'faculty']
    }


#CourseTree
class CourseLeaf(EmbeddedDocument):
	course = ReferenceField(Course)
	semester = IntField()
	meta = {
        'ordering': ['-sememster']
    }


class CourseTree(Document):
	_id = StringField(required=True, help_text='21kr流水號', primary_key=True)
	en_url = StringField(help_text='en_name encoded')
	ch_url = StringField(help_text='ch_name encoded')
	course_leaves = ListField(EmbeddedDocumentField(CourseLeaf))
	pilot_course = ReferenceField(Course)
	category = ReferenceField(Category)
	tri_indexes = ListField(IntField(default=0))
	comments = ListField(ReferenceField(Comment))
	def __unicode__(self):
		return '%s' % (self._id)

