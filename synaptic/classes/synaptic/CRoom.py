from channels.db import database_sync_to_async
from synaptic.models import QuizRoom, RoomStatus, QuizRoomMemberAnswer, Question, User, UserExtension
from synaptic.models import QuizRoomMember
from synaptic import constants
from synaptic.constants import RoomStatus as rs, ReturnCodes as rc
from datetime import datetime as dt

class CRoom():
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.DEBUG = False

       

    @database_sync_to_async
    def initialise(self, parent, room_number, User):
        self.parent = parent
        self.User = User
        self.room = QuizRoom.objects.get_or_none(room_number=room_number)
        if self.room is None:
            print ("<CRoom: init>: no room")
            return rc.FAILED

        self.user_is_host = False
        if self.User.user == self.room.host:
            self.user_is_host = True

        # set room status codes dictionary to reduce database load later
        status_rows =  RoomStatus.objects.all()
        self.status_dict = {row.description: row for row in status_rows}

        return rc.SUCCESS

    @database_sync_to_async
    def save_updated_question_answers(self, answers):
        self.room =  QuizRoom.objects.get_or_none(pk=self.room.pk)
        question = self.room.current_question

        changes = False
        for answer in answers:
            answer_state = answers.get(answer)
            if answer_state != getattr(question, answer):
                setattr(question, answer, answer_state)
                changes = True

        if changes:
            question.save()

    @database_sync_to_async
    def get_current_question_number(self):
        return self.room.current_question.question_number

    @database_sync_to_async
    def get_db_room(self):
        self.room =  QuizRoom.objects.get_or_none(pk=self.room.pk)

    @database_sync_to_async
    def get_last_question_number(self):
        return self.room.last_question.question_number

    @database_sync_to_async
    def get_live_room_status(self):
        self.room =  QuizRoom.objects.get_or_none(pk=self.room.pk)
        return self.room.status.description

    @database_sync_to_async
    def get_next_question(self):
        self.room =  QuizRoom.objects.get_or_none(pk=self.room.pk)
        current_question_number = self.room.current_question.question_number
        next_question = Question.objects.get_or_none(
            quiz=self.room.quiz, question_number = current_question_number + 1)
        self.room.previous_question = self.room.current_question
        self.room.current_question = next_question
        self.room.save()
        return self.room.status.description

    @database_sync_to_async
    def get_quiz(self):
        self.room =  QuizRoom.objects.get_or_none(pk=self.room.pk)
        return  self.room.quiz

    @database_sync_to_async
    def get_score_multiplier(self):
        return  self.room.current_question.score_multiplier

    #@database_sync_to_async
    def get_time_remaining(self):
        return min([self.room.current_question.time_limit, self.room.countdown_seconds_remaining])

    @database_sync_to_async
    def get_user_by_username(self, username):
        return User.objects.get(username=username)

    @database_sync_to_async
    def initialise_question(self):
        # reset time limit for question
        self.room =  QuizRoom.objects.get_or_none(pk=self.room.pk)
        self.room.countdown_seconds_remaining = self.room.current_question.time_limit
        self.room.save()
        # delete any existing answers for question
        member_answers = QuizRoomMemberAnswer.objects.filter(
            room=self.room, question_number__gte=self.room.current_question.question_number).delete()

    async def print_room_status(self, *args):
        room_status = await self.get_live_room_status()
        print (self.user.username, room_status, *args)

    @database_sync_to_async
    def restart_from_question(self, question_number):
        _question_number = int(question_number)
        self.room =  QuizRoom.objects.get_or_none(pk=self.room.pk)
        if _question_number <= 0 or _question_number > self.room.current_question.question_number:
            return False
        question = Question.objects.get_or_none(quiz=self.room.quiz, question_number = _question_number)
        if question is None:
            return False;
        previous_question = Question.objects.get_or_none(quiz=self.room.quiz, question_number = _question_number - 1)
        self.room.current_question = question
        self.room.previous_question = previous_question
        self.room.countdown_seconds_remaining = question.time_limit
        self.room.save()
        return True

    @database_sync_to_async
    def set_countdown(self, timer):
        self.room =  QuizRoom.objects.get_or_none(pk=self.room.pk)
        if self.room.status.description == rs.QUESTION:
            self.room.countdown_seconds_remaining = timer
            self.room.save()

    @database_sync_to_async
    def set_question_start_time(self):
        self.room =  QuizRoom.objects.get_or_none(pk=self.room.pk)
        self.room.question_start_time = dt.now().astimezone()
        self.room.save()

    async def set_status(self, status):
        if self.DEBUG:
            print (f"Setting status {self.user}, {status}")
        await self.set_room_status(status)

    @database_sync_to_async
    def set_room_status(self, status):
        if self.DEBUG:
            print (f"Setting room status {self.user}, {status}")
        self.room =  QuizRoom.objects.get_or_none(pk=self.room.pk)
        self.room.status = self.status_dict.get(status, None)
        if self.room.status == None:
            print(f"<CRoom: set_room_status>: room status {status} does not exist in RoomStatus table)")
        self.room.save()

