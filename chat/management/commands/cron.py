from django.core.management.base import BaseCommand, CommandError
from chat.models import *
import time
from datetime import datetime, date
from datetime import timedelta

class Command(BaseCommand):
	args = '<poll_id poll_id ...>'
	help = 'Closes the specified poll for voting'

	def handle(self, *args, **options):
		while 1:
			time.sleep(1)
			# See who needs to be pinged out
			userList=User.objects.filter(currentlyActive__exact=1).filter(lastSeen__lt=datetime.now() - timedelta(seconds = 120))
			if len(userList) > 0:
				for i in userList:
					i.currentlyActive = 0
					i.save()
					# See if we need to close the room
					usersInRoom = User.objects.filter(room__exact=i.room).filter(currentlyActive__exact=1)
					if not usersInRoom:
						linesToErase = TextLine.objects.filter(room__exact=i.room)
						for a in linesToErase:
							a.delete()
						usersInRoom = User.objects.filter(room__exact=i.room)
						for a in usersInRoom:
							a.delete()
						i.room.delete()
					else:
						line=TextLine()
						line.text = "Partner has left the chat. Connection was lost."
						line.user = None
						line.room = i.room
						line.save()
