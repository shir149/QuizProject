import json

from channels.generic.websocket import WebsocketConsumer

from channels.consumer import AsyncConsumer
from channels.exceptions import StopConsumer
from django.shortcuts import reverse
from django.http import HttpResponseRedirect
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from django.template.loader import render_to_string
from django.utils.safestring import SafeString
import channels_redis
from .models import User, QuizRoomMember, QuizRoom, RoomMemberStatus, Question, Answer, RoomStatus
from .models import Quiz, QuizRoomMemberAnswer
from .constants import MessageType as mt, MessageContent as mc, RoomStatus as rs, RoomMemberStatus as rms
from .constants import UserType as ut, ReturnCodes as rc
from .classes.synaptic.CUser import CUser
from .classes.synaptic.CRoom import CRoom
from .classes.synaptic.CRoomMember import CRoomMember
from .classes.synaptic.CMessage import CMessage
from .classes.synaptic.CContent import CWaitingState, CQuestionState, CQuestionPreviewState, CReturnToAnswersState
from .classes.synaptic.CContent import CResultsState, CAnswerState, CRestartState, CAmendAnswerState
from .classes.synaptic.CContent import CScoreMultiplierState
import requests_async as requests

from .classes.synaptic.CContent import CContent
import json
import sys
import time
#import traceback

class AppError(Exception):
    pass

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        self.send(text_data=json.dumps({"message": message}))


class QuizConsumer(AsyncConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.connected = False
        self.DEBUG = False

    async def accept_websocket(self):
        await self.send({
            "type": "websocket.accept"
        })

    async def close_websocket(self):
        await self.send({
            "type": "websocket.close"
        })

    async def broadcast_message(self, content: str) -> None:
        """
        Must be called with await \n
        Callback routine to forward a message sent with 'broadcast_message' type out on the websocket \n
        The calling function cannot send out on websocket directly as the websocket send must be asynchronous

        :param content: the content to be sent out.  This is converted to json before send
        :return: When called asynchronously, None
        """
        # send the actual message
        await self.send ({
            "type": "websocket.send",
            "text": json.dumps(content)
        })

    async def get_received_data(self, event):
        data = event.get('text', None)
        if data is None:
            return

        received_data_dict = json.loads(data)
        type = received_data_dict.get("type")
        text = received_data_dict.get("value")
        return type, text

    async def redirect_websocket(self, url):
        print (f"redirecting websocket for {self.User.user.username} to {url}")
        await self.send({
            "type": mt.BODY,
            "html": "<script>window.location.replace(url);</script>"
        })

    def get_room_number(self) -> int:
        """
        Extracts the room number for the url of the page
        :return: room number
        """
        path_frags = self.scope['path_remaining']
        return path_frags.split('/')[-1]

    def get_scope_username(self) -> str:
        """
        Returns the username for the logged in authenticated user
        :return: username if logged in and authenticated, otherwise 'Anonymous'
        """
        user = self.scope['user']
        username = "Anonymous"
        if user.is_authenticated:
            username = user.username
        return username

    async def initialise_instance_variables(self) -> None:
        """
        Must be run with await
        Initialises Consumer instance variables: self.User; self.Room; self.room_member,
        self.message and self.content;
        :return: when called asynchronously, None
        """
        # initialise User object as wrapper around user model
        self.User = CUser()
        await self.User.initialise(self.get_scope_username())

        #initialise Room object as wrapper around the room model
        self.Room = CRoom()
        if await self.Room.initialise(self, self.get_room_number(), self.User) == rc.FAILED:
            return rc.FAILED

        self.Room_member = CRoomMember(self.Room, self.User)
        await self.Room_member.initialise()
        self.message = CMessage(self, self.Room, self.User, self.Room_member)
        await self.message.initialise()
        #self.content = CContent(self)

        self.amend_answer_state      = CAmendAnswerState(
            self, self.Room, self.User, self.Room_member, self.message)
        self.answer_state            = CAnswerState(
            self, self.Room, self.User, self.Room_member, self.message)
        self.question_preview_state  = CQuestionPreviewState(
            self, self.Room, self.User, self.Room_member, self.message)
        self.question_state          = CQuestionState(
            self, self.Room, self.User, self.Room_member, self.message)
        self.results_state           = CResultsState(
            self, self.Room, self.User, self.Room_member, self.message)
        self.waiting_state           = CWaitingState(
            self, self.Room, self.User, self.Room_member, self.message)
        self.restart_state           = CRestartState(
            self, self.Room, self.User, self.Room_member, self.message)
        self.return_to_answers_state = CReturnToAnswersState(
            self, self.Room, self.User, self.Room_member, self.message)
        self.score_multiplier_state = CScoreMultiplierState(
            self, self.Room, self.User, self.Room_member, self.message)


        return rc.SUCCESS

    async def send_content(self, received_param=None, disconnecting=False):
        status = await self.Room.get_live_room_status()
        if status == rs.WAITING:
            await self.waiting_state.send_content(received_param)
        elif status == rs.QUESTION_PREVIEW:
            await self.question_preview_state.send_content(received_param)
        elif status == rs.QUESTION:
            await self.question_state.send_content(received_param)
        elif status == rs.ANSWER:
            await self.answer_state.send_content(received_param)
        elif status == rs.RESULTS:
            await self.results_state.send_content(received_param)
        elif status == rs.SCORE_MULTIPLIER:
            await self.score_multiplier_state.send_content(received_param)
        else:
            print ("Undefined room state - no messages sent")

    async def websocket_connect(self, event: object) -> None:
        """
        Callback method - called when a websocket connect event occurs
        :param event: the event object provided by the websocket
        """
        self.connected = False
        if await self.initialise_instance_variables() == rc.FAILED:
            print(f"initialisation failed for user {self.User.user.username} - websocket disconnected")
            await self.redirect_websocket('/synaptic/join_room/')
            await self.close_websocket()
            return
        if self.DEBUG:
            await self.room.print_room_status("Connected", self.channel_name, event)

        await self.accept_websocket()

        self.connected = True

        # send messages to affected members/host
        await self.send_content()

    async def websocket_receive(self, received_message: str) -> None:
        """
        Callback method, called when a message is received on the websocket
        :param received_message: the message received from the websocket
        :return: None
        """
        if self.DEBUG:
            print ("receive", self.User.user.username, self.channel_name, received_message)
        type, received_param = await self.get_received_data(received_message)

        if self.Room.user_is_host:
            # host only
            # start-quiz-button is on the question-preview page
            # next-question-button is on the results page
            if type == 'preview-done-button':
                return_url = self.scope['session']['preview_return_to_url']
                await self.message.send_preview_complete_message(reverse(f"synaptic:{return_url}"))
                return
            if type == 'preview-next-button':
                await self.Room.get_next_question()
                await self.Room.set_status(rs.QUESTION_PREVIEW)
                await self.send_content()
                await self.message.send_timer_message(mc.START_TIMER)
            if type == 'restart-quiz-button':
                await self.restart_state.send_content(received_param, disconnecting=False)
            if type == 'return-to-waiting-button':
                await self.send_content()
            if type == 'amend-answer-button':
                await self.amend_answer_state.send_content(received_param, disconnecting=False)
            if type == 'return-to-answers':
                error = await self.return_to_answers_state.send_content(received_param, disconnecting=False)
                if len(error) == 0:
                    await self.Room.save_updated_question_answers(received_param)
                    await self.send_content()
            if type == 'restart-from-question':
                rc = await self.Room.restart_from_question(received_param)
                if not rc:
                    await self.send_content()
            if type in ['start-quiz-button', 'next-question-button', 'restart-from-question', 'score-multiplier-end']:
                status = None
                if await self.Room.get_live_room_status() != rs.SCORE_MULTIPLIER:
                    if type == 'next-question-button' and self.Room.get_live_room_status():
                        await self.Room.get_next_question()
                        #self.room = await self.room.get_db_room()
                    await self.Room.initialise_question()
                    await self.Room_member.reset_joker_status()
                    # initiate preview for question
                    score_multiplier = await self.Room.get_score_multiplier()
                    if score_multiplier == 1:
                        status = rs.QUESTION_PREVIEW
                    else:
                        status = rs.SCORE_MULTIPLIER
                else:
                    status = rs.QUESTION_PREVIEW
                await self.Room.set_status(status)
                # send messages to affected members/host
                await self.send_content()
                # send websocket message to start the timer (timer only runs in host webpage)
                if status == rs.QUESTION_PREVIEW:
                    await self.message.send_timer_message(mc.START_TIMER)
            elif type == 'results-button':
                # results button on answers page has been pressed by host
                await self.Room_member.set_db_member_scores()
                await self.Room.set_status(rs.RESULTS)
                await self.send_content()
            elif type == 'countdown' or type == 'preview-skip-button':
                # countdown message has been received from host webpage
                if type == 'countdown':
                    count_value = received_param
                if type == 'preview-skip-button' or int(count_value) <= 0:
                    #initiate next action if countdown has reached 0
                    await self.message.send_timer_message(mc.STOP_TIMER)
                    status = await self.Room.get_live_room_status()
                    if status == rs.QUESTION_PREVIEW:
                        await self.Room.set_status(rs.QUESTION)
                        await self.Room.initialise_question()
                        await self.send_content()
                        await self.message.send_timer_message(mc.START_TIMER)
                        await self.Room.set_question_start_time()
                        return
                    elif status == rs.QUESTION:
                        await self.Room.set_status(rs.ANSWER)
                        await self.send_content()
                        await self.Room_member.set_db_member_answers_timeout()
                else:
                    # send out countdown message to all members to trigger update of screen countdown
                    # save countdown value to db in case of restart - consider scrapping this:
                    # not sure it is adding much value for so many db writes
                    await self.Room.set_countdown(count_value)
                    await self.message.send_countdown_message(count_value)

        else:
            # all members
            if type == 'joker-button':
                await self.Room_member.set_joker_status(received_param)
            if type == 'answer':
                # process answer message submitted by member
                answer_number = received_param
                await self.Room.get_db_room()
                await self.Room_member.set_db_member_answer(answer_number)
                await self.message.send_answer_status_message()
                if await self.Room_member.all_answers_received():
                    await self.Room.set_status(rs.ANSWER)
                    await self.message.send_timer_message(mc.STOP_TIMER)
                    await self.send_content()

    async def websocket_disconnect(self, event: object) -> None:
        """
         Callback method - called when a websocket disconnect event occurs
         :param event: the event object provided by the websocket
        """
        if self.connected:
            if self.DEBUG:
                print ("disconnected", self.User.user.username, self.channel_name, event)
            await self.Room_member.set_member_status(rms.LEFT)
            # throw everyone out of the room if the host disconnects
            if self.Room.user_is_host:
                await self.Room.set_status(rs.WAITING)
            # send messages to affected members/host
            await self.send_content(disconnecting=True)
            # remove self from websocket broadcast groups
            await self.message.remove_from_broadcast_groups()
            if self.DEBUG:
                print ("End of disconnect")

        self.connected = False
        raise StopConsumer()