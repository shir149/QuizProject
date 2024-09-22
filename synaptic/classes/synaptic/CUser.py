from channels.db import database_sync_to_async
from synaptic.models import User, UserExtension
from synaptic.constants import RoomMemberStatus as rms

class CUser():
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

 

    @database_sync_to_async
    def initialise(self, username):
        self.user = User.objects.get(username=username)

