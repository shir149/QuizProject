from channels.db import database_sync_to_async
from django.db.models import Count
from synaptic.models import QuizRoomMember, RoomMemberStatus, QuizRoomMemberAnswer, Answer, QuizRoom
from synaptic.constants import RoomMemberStatus as rms, Constants
from datetime import datetime as dt

class CRoomMember():
    def __init__(self, Room, User):
        super().__init__()
        self.Room = Room
        self.User = User
        self.constants = Constants()

        

    async def initialise(self):
        await self.set_status_codes_dict()
        await self.set_member_status(rms.JOINED)

    async def all_answers_received(self):
        answers_count = await self.get_answers_count_async()
        # members count does not include host
        members_count = await self.get_members_count_async(rms.JOINED) - 1
        if answers_count == members_count:
            return True
        return False

    # @database_sync_to_async
    # def delete_db_room_members(self):
    #     status = RoomMemberStatus.objects.get_or_none(description=rms.LEFT)
    #     QuizRoomMember.objects.filter(room = self.room, status=status).all().delete()

    @database_sync_to_async
    def get_answers_count_async(self) -> int:
        """
        Gets count of all submitted answers (all room members) for current question
        :return: count of submitted answers to current question
        """

        count = self.get_answers_count_sync()
        # #room_members = QuizRoomMember.objects.filter(room=self.Room.room).all()
        # count = QuizRoomMemberAnswer.objects.filter(
        #     room=self.Room.room, question=self.Room.room.current_question).count()
        return count

    def get_answers_count_sync(self) -> int:
        """
        Gets count of all submitted answers (all room members) for current question
        :return: count of submitted answers to current question
        """
        #room_members = QuizRoomMember.objects.filter(room=self.Room.room).all()
        count = QuizRoomMemberAnswer.objects.filter(
            room=self.Room.room, question=self.Room.room.current_question).count()
        return count

    @database_sync_to_async
    def get_members_count_async(self, status) -> int:
        """
        Gets count of all members in room with joined status.  \n
        Note this does not include the host
        :return: count of members in room with joined status
        """
        count = self.get_members_count_sync(status)
        # filters = {"room": self.Room.room}
        # if status in [rms.LEFT, rms.JOINED]:
        #     filters["status"] = self.status_dict.get(status, None)
        # count = QuizRoomMember.objects.filter(**filters).count()
        return count

    def get_members_count_sync(self, status) -> int:
        """
        Gets count of all members in room with joined status.  \n
        Note this does not include the host
        :return: count of members in room with joined status
        """
        filters = {"room": self.Room.room}
        if status in [rms.LEFT, rms.JOINED]:
            filters["status"] = self.status_dict.get(status, None)
        count = QuizRoomMember.objects.filter(**filters).count()
        return count

    @database_sync_to_async
    def set_member_status(self, status: str) -> None:
        """
        Must be called using await
        Update room member status
        :param status: a room member status constant, rms.JOINED or rms.LEFT
        :return: if called asynchronously, None
        """
        if status not in [rms.JOINED, rms.LEFT]:
            print (f"<CRoomMember: set_member_status>: invalid status received: {status}")
            return

        # get existing room member if any, otherwise create new
        self.room_member = QuizRoomMember.objects.get_or_none(user=self.User.user, room=self.Room.room)
        if self.room_member is None:
            print (f"Room member does not exist - this should never happen. User is {self.user.username}, room is {self.Room.room.room_number}")

        # update status
        self.room_member.status = self.status_dict.get(status, None)
        self.room_member.save()

    @database_sync_to_async
    def set_db_member_answer(self, answer_number):
        self.room_member = QuizRoomMember.objects.get_or_none(user=self.User.user, room=self.Room.room)
        current_question = self.Room.room.current_question
        # ignore joker if malicious user has not submitted more jokers than they are entitled to
        jokers_played = QuizRoomMemberAnswer.objects.filter(
            room_member=self.room_member, question=current_question, joker_status=True).count()
        if jokers_played >= self.constants.MAX_JOKERS:
            self.room_member.joker_status = False

        member_answer = QuizRoomMemberAnswer.objects.get_or_none(
            room=self.Room.room, user=self.User.user, question=current_question)
        if member_answer is not None:
            member_answer.delete()
        response_time = (dt.now().astimezone() - self.Room.room.question_start_time).total_seconds()
        room_member_answer = QuizRoomMemberAnswer(
            room_member=self.room_member, room=self.Room.room, user=self.User.user,
            question=current_question, response_time=response_time, running_score_prior=0,
            question_number=current_question.question_number,
            joker_status=self.room_member.joker_status)
        room_member_answer.answer_number = answer_number
        room_member_answer.save()

    @database_sync_to_async
    def set_db_member_answers_timeout(self):
        current_question = self.Room.room.current_question
        # find all answers submitted by room members
        responses = QuizRoomMemberAnswer.objects.filter(
            room=self.Room.room, question=self.Room.room.current_question).all()
        responders = [response.user for response in responses]
        # get all room members who did not respond
        non_responders = QuizRoomMember.objects.filter(room=self.Room.room).exclude(user__in=responders).\
            exclude(user=self.Room.room.host)
        # create a default response for each non-responder
        for non_responder in non_responders:
            room_member_answer = QuizRoomMemberAnswer(
                room_member=non_responder, room=self.Room.room, user=non_responder.user,
                question=current_question, answer_score=0, running_score_prior=0,
                question_number=current_question.question_number,
                joker_status=non_responder.joker_status)
            prev_answer = QuizRoomMemberAnswer.objects.get_or_none(
                room_member=non_responder, question=self.Room.room.previous_question)
            if prev_answer is not None:
                room_member_answer.running_score_prior = prev_answer.running_score
            room_member_answer.running_score = room_member_answer.running_score_prior
            room_member_answer.save()

    @database_sync_to_async
    def set_db_member_scores(self):
        """
        Set db member scores for the round
        """
        current_question = self.Room.room.current_question
        # get member answers for the current question
        member_answers = QuizRoomMemberAnswer.objects.filter(
            room=self.Room.room, question=current_question)
        for member_answer in member_answers:
            # get answer to previous question to access prior running score
            # prev_answer = QuizRoomMemberAnswer.objects.get_or_none(
            #     room_member=member_answer.room_member, question=self.Room.room.previous_question)
            prev_answer = QuizRoomMemberAnswer.get_previous_answer(member_answer.room_member, current_question)
            # prev_answer is None implies start of quiz
            if prev_answer is not None:
                # get running score from previous answer
                member_answer.running_score_prior = prev_answer.running_score
            member_answer.answer_score = 0
            # if member submitted answer to question
            if member_answer.answer_number is not None:
                # calculate score for correct answer
                if getattr(current_question, f"correct_answer_{member_answer.answer_number}") == True:
                    member_answer.answer_score = \
                        int(round((1 - (float(member_answer.response_time)/current_question.time_limit)/2) *
                                    1000 * float(current_question.score_multiplier),0)) * \
                                    (member_answer.joker_status + 1)
            # set new carry-forward running score
            member_answer.running_score = \
            member_answer.running_score_prior   + member_answer.answer_score
            member_answer.save()

    @database_sync_to_async
    def set_joker_status(self, status):
        joker_status = False
        if status == 'true':
            joker_status = True

        self.room_member = QuizRoomMember.objects.get_or_none(user=self.User.user, room=self.Room.room)
        if self.room_member is None:
            print (f"Room member does not exist - this should never happen. User is {self.user.username}, room is {self.Room.room.room_number}")

        # update status
        self.room_member.joker_status = joker_status
        self.room_member.save()
        x=1

    @database_sync_to_async
    def reset_joker_status(self):
        # reset joker status on all room members
        QuizRoomMember.objects.filter(room=self.Room.room).update(joker_status=False)

    @database_sync_to_async
    def set_status_codes_dict(self):
        # set room member status codes disctionary to reduce database load later
        status_rows =  RoomMemberStatus.objects.all()
        self.status_dict = {row.description: row for row in status_rows}
