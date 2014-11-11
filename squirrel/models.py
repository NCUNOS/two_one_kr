# coding=UTF8
from mongoengine.django.auth import User
from mongoengine import *

# Create your models here.

class User(User):
	std_id = IntField(help_text='學號')
	nick_name = StringField(help_text='顯示名稱')	
	def __unicode__(self):
		return '[#%s] %s / %s <br/>' % (self.pk, self.nick_name, self.std_id)
	USERNAME_FIELD = 'username'
	REQUIRED_FIELDS = ['nick_name']