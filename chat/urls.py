from django.conf.urls.defaults import *
from djangoapps.chat.models import *

urlpatterns = patterns('djangoapps.chat.views',
   (r'^room/(?P<roomName>[^/]+)/$', "chatWindow"),
   (r'^room/(?P<roomName>[^/]+)/getnext$', "getnext"),
   (r'^room/(?P<roomName>[^/]+)/commandStream$', "commandStream"),
   (r'^room/(?P<roomName>[^/]+)/sendline$', "sendline"),
   (r'^createRoom', "createRoom"),
   (r'^$', "front"),
)
