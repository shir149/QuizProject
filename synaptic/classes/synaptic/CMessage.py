from synaptic.models import QuizRoom
from synaptic.constants import SendGroup as sg, MessageType as mt, MessageContent as mc
from channels.db import database_sync_to_async
from synaptic.constants import Constants, RoomStatus as rs
from synaptic.constants import RoomMemberStatus as rms
import json
import sys

class CMessage():
    def __init__(self, parent, Room, User, Room_member, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = parent
        self.Room = Room
        self.User = User
        self.Room_member = Room_member
        self.channel_name = self.parent.channel_name
        self.bg_all = f"{self.Room.room.room_number}"
        self.bg_me = f"{self.Room.room.room_number}-{self.User.user.username}"
        self.bg_members = f"{self.Room.room.room_number}-members"
        self.bg_host = f"{self.Room.room.room_number}-host"

        self.groups_dict = {sg.ALL: self.bg_all, sg.ME: self.bg_me,
                            sg.MEMBER: self.bg_members, sg.HOST: self.bg_host}
        self.constants = Constants()

        self.DEBUG = False

    async def initialise(self):
        await self.add_to_broadcast_groups()

    async def add_to_broadcast_groups(self) -> None:
        """
        Must be called using await \n
        Requires self.<broadcast groups> to be set \n
        Adds user to the appropriate broadcast groups (channel layer send groups)

        :return: When called asynchronously, None
        """
        # add to group for everyone
        await self.parent.channel_layer.group_add(
            self.bg_all,
            self.channel_name
        )
        # add to group for me
        await self.parent.channel_layer.group_add(
            self.bg_me,
            self.channel_name
        )
        # add to group for members (excludes host)
        if self.Room.user_is_host:
            await self.parent.channel_layer.group_add(
                self.bg_host,
                self.channel_name)
        else:
            await self.parent.channel_layer.group_add(
                self.bg_members,
                self.channel_name
            )

    @database_sync_to_async
    def calc_time_remaining(self):
        return min([self.Room.room.current_question.time_limit, self.Room.room.countdown_seconds_remaining])

    async def remove_from_broadcast_groups(self):
        # add to group for everyone
        if self.DEBUG:
            print (f"Removing {self.User.user.username} from {self.bg_all}, channel: {self.channel_name}")
        await self.parent.channel_layer.group_discard(
            self.bg_all,
            self.channel_name
        )
        # add to group for me
        if self.DEBUG:
            print (f"Removing {self.User.username} from {self.bg_me}, channel: {self.channel_name}")
        await self.parent.channel_layer.group_discard(
            self.bg_me,
            self.channel_name
        )
        # add to group for members (excludes host)
        if not self.Room.user_is_host:
            if self.DEBUG:
                print (f"Removing {self.User.user.username} from {self.bg_members}, channel: {self.channel_name}")
            await self.parent.channel_layer.group_discard(
                self.bg_members,
                self.channel_name
            )

    async def send_answer_status_message(self):
        answer_count = await self.Room_member.get_answers_count_async()
        # member count excludes host
        member_count = await self.Room_member.get_members_count_async(rms.JOINED) -1

        data = json.dumps({"answer_status": f"Answers: {answer_count}/{member_count}"})
        await self.send_message(sg.ALL, mt.ANSWER_STATUS, data=data)

    async def send_countdown_message(self, count_value):
        data = json.dumps({"count_value": count_value})
        await self.send_message(sg.ALL, mt.COUNTDOWN, data=data)

    async def send_message(self, group, message_type, html=None, data=None, animation="None"):
        broadcast_group = self.groups_dict.get(group, None)
        if broadcast_group is None:
            print (f"Unrecognised broadcast group for sending: {group}")
            return

        if self.DEBUG:
            print ("Sending message", self.User.user.username, broadcast_group, message_type, data)

        await self.parent.channel_layer.group_send (
            broadcast_group,
            {
                "type": 'broadcast_message',
                "content_type": message_type,
                "html": html,
                "data": data,
                "animation": animation
            }
        )

    async def send_preview_complete_message(self, url):
        data = json.dumps({"url": url})
        await self.send_message(sg.HOST, mt.PREVIEW_COMPLETE, data=data)

    async def send_timer_message(self, timer_action):
        if timer_action == mc.STOP_TIMER:
            data = json.dumps({"type": mc.STOP_TIMER})
            await self.send_message(sg.HOST, mt.TIMER, data=data)

        if not self.Room.user_is_host:
            return

        if timer_action == mc.START_TIMER:
            status = await self.Room.get_live_room_status()
            time_remaining = self.constants.PREVIEW_TIMEOUT
            if status == rs.QUESTION:
                time_remaining = await self.calc_time_remaining()
            if time_remaining > 0:
                data = json.dumps({"type": mc.START_TIMER, "time_limit": time_remaining})
                await self.send_message(sg.ME, mt.TIMER, data=data)

