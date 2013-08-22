import time
from datetime import datetime, date
from calendar import month_name
from datetime import timedelta

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.utils.html import escape
from django.utils.encoding import iri_to_uri

from djangoapps.chat.models import *
from django.forms import ModelForm
from django.db import transaction
import urllib

def getUser(request, roomName):
	roomName = roomName[:128]
	# Make sure the user has a cookie set
	if 'sessionId' in request.session:
		# Make sure the session id exists
		try:
			newSession = UserSession.objects.get(pk=request.session['sessionId'])
		except UserSession.DoesNotExist:
			return None
		# Check to see if there is a user instance for this room already
		user = User.objects.filter(room__name__exact=roomName).filter(session__exact=newSession)
		if not user:
			return None
		user = user[0]
		# Make sure the user is currently active
		if user.currentlyActive != 1:
			return None
		return user
	return None

def chatWindow(request, roomName):
	roomName = roomName[:128]

	# Check to see if a cookie is already set
	if not ('sessionId' in request.session):
		# If there's no cookie, create a new session and user
		newSession = UserSession()
		newSession.save()
		request.session['sessionId'] = newSession.pk
	else:
		# Make sure the session instance exists in the databse
		try:
			newSession = UserSession.objects.get(pk=request.session['sessionId'])
		except UserSession.DoesNotExist:
			return HttpResponse("")		# user must have an old cookie

		# Check to see if there is a user instance for this room already
		user = User.objects.filter(room__name__exact=roomName).filter(session__exact=newSession)
		if user:
			user = user[0]
			# Make sure the user is currently active
			if user.currentlyActive != 1:
				return HttpResponse("This room is already occupied.")
			return render_to_response("list.html", {'user':user}, context_instance=RequestContext(request))

	# if there's no room, create it
	room = Room.objects.filter(name__exact=roomName)
	if not room:
		room = Room()
		room.name = roomName
		room.save()
	else:
		room = room[0]
		roomSize = User.objects.filter(room__exact=room)
		if roomSize != 0:
			if len(roomSize) > 1:
				return HttpResponse("This room is already occupied.")
	# there's no user, so create one
	newUser = User()
	newUser.currentlyActive = 1
	newUser.session = newSession
	newUser.room = room
	newUser.save()
	line=TextLine()
	line.text = "User has joined the chat."
	line.user = None
	line.room = room
	line.save()
	return render_to_response("list.html", {'user':newUser}, context_instance=RequestContext(request))

def commandStream(request, roomName):
	roomName = roomName[:128]
	user = getUser(request, roomName)
	if user == None:
		return HttpResponse("")
	pingCounter = 0
	while 1:
		if user.currentlyActive == 0:
			return HttpResponse("")
		if TextLine.objects.filter(room__exact=user.room).latest('pk').pk > user.lastUpdatedChat:
			return HttpResponse("1")
		if pingCounter == 55:
			return HttpResponse("")
		pingCounter += 1
		user = User.objects.get(pk=user.pk)
		user.lastSeen = datetime.now()
		if user.floodCount > 5:
			user.floodCount = 5
		else:
			if user.floodCount != 0:
				user.floodCount -= 1
		user.save()
		time.sleep(1)

def getnext(request, roomName):
	roomName = roomName[:128]
	user = getUser(request, roomName)
	if user != None:
		user.lastUpdatedChat = TextLine.objects.filter(room__exact=user.room).latest('pk').pk
		user.save()
		line=TextLine.objects.filter(room__exact=user.room).order_by('pk')
		outputString = ""
		for i in line:
			if i.user == None:		# the "from" field is blank, so it's a server notice, instead of a message from a specific user
				outputString += i.timestamp.__str__() + " <b>" + i.text + '</b><br>'
			else:
				if i.user == user:
					outputString += i.timestamp.__str__() + " <b>You:</b> " + i.text + '<br>'
				else:
					outputString += i.timestamp.__str__() + " <b>Partner:</b> " + i.text + '<br>'
		return HttpResponse(outputString)
	return HttpResponse("")

def sendline(request, roomName):
	roomName = roomName[:128]
	user = getUser(request, roomName)
	if user != None:
		if user.verifyUser() != 0:
			return HttpResponse("")
		input = escape(request.POST['text'])
		line=TextLine()
		line.text = escape(request.POST['text'])
		line.user = user
		line.room = user.room
		line.save()
		room = Room.objects.all()[0]
		room.save()
		return HttpResponse("")
	return HttpResponse("")

def front(request):
	return render_to_response("front.html", context_instance=RequestContext(request))

def createRoom(request):
	return HttpResponseRedirect("./room/" + urllib.quote(iri_to_uri(request.POST['roomName']), "") + "/")
