from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from django.core.mail import send_mail

class User(models.Model):
	lastSeen = models.DateTimeField(auto_now_add=True, db_index=True)
	lastUpdatedChat = models.IntegerField(default='0')
	currentlyActive = models.BooleanField(db_index=True)
	room = models.ForeignKey('Room', db_index=True)
	session = models.ForeignKey('UserSession')
	floodCount = models.IntegerField(default='0')
	def verifyUser(self):
		if self.floodCount >= 3:
			return 1
		self.floodCount += 1
		self.save()
		return 0

class TextLine(models.Model):
	text = models.CharField(max_length=256)
	timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
	user = models.ForeignKey(User, null=True)
	room = models.ForeignKey('Room', db_index=True)

class Room(models.Model):
	name = models.CharField(max_length=128, db_index=True)

class UserSession(models.Model):
	pass
