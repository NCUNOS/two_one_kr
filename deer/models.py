# coding=UTF8
from mongoengine import *

from spider.models import *
from squirrel.models import *

import datetime

# Create your models here.
class Msg(EmbeddedDocument):
	text = StringField(max_length=125, required=True)
	left_by = ReferenceField(User)
	date = DateTimeField(default=datetime.datetime.now)
	meta = {
        'ordering': ['-date']
    }

class Comment(Document):
	text = StringField(required=True)
	msgs = ListField(EmbeddedDocumentField(Msg))
	push_num = IntField(default=1)
	date = DateTimeField(default=datetime.datetime.now)
	elements = ListField(StringField())
	left_by = ReferenceField(User)
	tri_indexes = ListField(IntField())
	
	meta = {
        'ordering': ['-date']
    }

	