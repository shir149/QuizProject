from channels.db import database_sync_to_async
from django.db.models import Count
from django.conf import settings
from synaptic.models import QuizRoomMemberAnswer, QuizRoomMember, Question, TransitionType, RoomMemberStatus
from django.template.loader import render_to_string
from django.db.models import F
from synaptic import functions as fn
from synaptic.constants import MessageType as mt, MessageContent as mc, UserType as ut
from synaptic.constants import SendGroup as sg, DefaultImages as di, Constants as c
from synaptic.constants import RoomStatus as rs, AnimationType as at, RoomMemberStatus as rms
from synaptic.functions import isEmpty
from synaptic.constants import Constants
import json
import random
import sys

class CContent():
    def __init__(self, parent, Room, User, Room_member, message):
        self.Room = Room
        self.User = User
        self.Room_member = Room_member
        self.message = message
        self.template_folder = "synaptic/live_room_templates"
        self.colours = {
            1: "#e21b3c",
            2: "#1368ce",
            3: "#d89e00",
            4: "#26890c"
        }
        self.constants = Constants()

        self.DEBUG = False

class CAmendAnswerState(CContent):
    def __init__(self, parent, Room, Room_member, Message, *args, **kwargs):
        super().__init__(parent, Room, Room_member, Message, *args, **kwargs)

        self.DEBUG = False
        self.template_folder += "/amend_answer"
        self.di = di()

    @database_sync_to_async
    def _create_body_host(self, user_type) -> str:
        """
        Must be called with await. \n
        Renders dynamic webpage body content, depending on messager_content parameter

        :param message_content: mc.WAITING_ROOM or mc.QUESTION to define content
        :param user_type: mc.ALL, ut.MEMBER, ut.HOST to define content
        :return: when called asyncronously, content string to be sent via websocket to webpage
        """

       
        question = Question.objects.get(pk=self.Room.room.current_question.id)
        answer_set, answer_list, answer_status, answer_totals, answer_text_size = \
            fn.get_answer_list(question, self.colours)

        # render the content to string
        html = render_to_string(f"{self.template_folder}/body_host.html", {
            'question': self.Room.room.current_question,
            'answers': answer_list,
            'answer_text_size': answer_text_size
        })

        return html

    @database_sync_to_async
    def _create_footer_host(self) -> None:
        """
        Must be called with await. \n
        Renders dynamic webpage body content, depending on messager_content parameter

        :param message_content: mc.WAITING_ROOM or mc.QUESTION to define content
        :param user_type: mc.ALL, ut.MEMBER, ut.HOST to define content
        :return: when called asyncronously, content string to be sent via websocket to webpage
        """

        html = render_to_string(f"{self.template_folder}/footer_host.html", {
        })
        return html

    async def _create_header_host(self) -> None:
        """
        Must be called with await. \n
        Renders dynamic webpage header content, depending on messager_content and user_type parameters

        :param message_content: mc.WAITING_ROOM or mc.QUESTION to define content
        :param user_type: ut.ALL, ut.MEMBER or ut.HOST
        :return: whem called asyncronously, content string to be sent via websocket to webpage
        """
        quiz = await self.Room.get_quiz()
        # answers_expected = await self.Room_member.get_members_count(status = rms.JOINED) - 1
        # answer_count = await self.Room_member.get_answers_count()
        # time_remaining = await self.Room.get_time_remaining()
        content = render_to_string(f"{self.template_folder}/header_host.html", {
            'quiz': quiz
            # 'answer_status': f"{answer_count}/{answers_expected}",
            # 'time_limit': time_remaining
        })

        return content

    async def _send_content(self, received_param:str, disconnecting:bool =False) -> None:
        if self.DEBUG:
            print (f"{self.Room.room.user.username} amend answer state messages")
        if self.Room.user_is_host:
            header = await self._create_header_host()
            await self.message.send_message(sg.HOST, mt.HEADER, html=header)

            body = await self._create_body_host(ut.HOST)
            await self.message.send_message(sg.HOST, mt.AMEND_ANSWERS_SCRIPT, html=body)

            footer = await self._create_footer_host()
            await self.message.send_message(sg.HOST, mt.FOOTER, html=footer)

    async def send_content(self, received_param:str, disconnecting=False):
        status = await self.Room.get_live_room_status()
        if status == rs.ANSWER:
            await self._send_content(received_param, disconnecting)

class CAnswerState(CContent):
    def __init__(self, parent, Room, Room_member, Message, *args, **kwargs):
        super().__init__(parent, Room, Room_member, Message, *args, **kwargs)

        self.DEBUG = False
        self.template_folder += "/answer"

    @database_sync_to_async
    def _create_body(self, user_type) -> tuple:
        """
        Must be called with await. \n
        Renders dynamic webpage body content for the answers page

        :param user_type: mc.ALL, ut.MEMBER, ut.HOST to define content
        :return: when called asyncronously, content string to be sent via websocket to webpage
        """

        # create 2 dictionaries from the question answers.
        # answer_status contains whether the answer is correct or not
        # answer_totals is initialised to hold the count of how many members selected that answer
        # answers = Answer.objects.filter(question = self.Room.room.current_question).all()
        # answer_list = [{
        #     "answer": answer.answer,
        #     "answer_number": answer.answer_number,
        #     "answer_colour": self.colours.get(answer.answer_number, '#7f7f7f')
        # }
        #     for answer in answers]
        question = Question.objects.get(pk=self.Room.room.current_question.id)
        answer_set, answer_list, answer_status, answer_totals, answer_text_size = \
            fn.get_answer_list(question, self.colours)

        # for answer in answers:
        #     answer_status[answer.answer_number] = answer.correct_answer
        #     answer_totals[answer.answer_number] = 0

        # populate answer_totals from the answers provided by the members
        #room_members = QuizRoomMember.objects.filter(room=self.Room.room).all()
        member_data = {}
        member_answers = QuizRoomMemberAnswer.objects.filter(
            room=self.Room.room, question=self.Room.room.current_question).all()
        for answer in member_answers:
            if answer is not None and answer.answer_number is not None:
                member_data[answer.room_member.nickname] = {"answer": f"answer-btn{answer.answer_number}"}
                answer_totals[answer.answer_number] += 1

        # create 2 lists to be passed to chart.js.  One holds the data (which is the answer totals).
        # The other holds the colours to be used in the chart
        dataset = []
        colours = []
        labels = []
        result_labels = []
        for i, answer in enumerate(answer_set[:len(answer_list)]):
            dataset.append(answer_totals[i + 1])
            colours.append(self.colours.get(i + 1, '#7f7f7f'))
            labels.append('')
            label = str(answer_totals[i + 1])
            if answer_status[i + 1] == True:
                label += " \u2713"
            result_labels.append(label)

        max_y = max(dataset) + 1

        html = render_to_string(f"{self.template_folder}/body.html", {
            'question': self.Room.room.current_question,
            'answers': answer_list,
            'answer_text_size': answer_text_size,
            'host': True
        })

        data = json.dumps({"data": dataset, "colours": colours, "result_labels": result_labels,
                           "labels": labels, "max_y": max_y, "member_data": member_data})
        return html, data

    @database_sync_to_async
    def _create_footer_host(self) -> None:
        """
        Must be called with await. \n
        Renders dynamic webpage body content, depending on messager_content parameter

        :param message_content: mc.WAITING_ROOM or mc.QUESTION to define content
        :param user_type: mc.ALL, ut.MEMBER, ut.HOST to define content
        :return: when called asyncronously, content string to be sent via websocket to webpage
        """

        html = render_to_string(f"{self.template_folder}/footer_host.html", {
            'room': self.Room.room
        })
        return html

    async def _create_header(self) -> None:
        """
        Must be called with await. \n
        Renders dynamic webpage header content, depending on messager_content and user_type parameters

        :param message_content: mc.WAITING_ROOM or mc.QUESTION to define content
        :param user_type: ut.ALL, ut.MEMBER or ut.HOST
        :return: whem called asyncronously, content string to be sent via websocket to webpage
        """
        question_number = await self.Room.get_current_question_number()
        html = render_to_string(f"{self.template_folder}/header.html", {
            'question_number': question_number,
        })

        return html

    async def _send_content(self, received_param:str, disconnecting:bool =False) -> None:
        if self.DEBUG:
            print (f"{self.Room.user.username} sending results state messages")

        html = await self._create_header()
        await self.message.send_message(sg.ALL, mt.HEADER, html=html)

        html, data = await self._create_body(ut.HOST)
        await self.message.send_message(sg.ALL, mt.ANSWERS_SCRIPT, html=html, data=data, animation=at.NONE)

        footer = await self._create_footer_host()
        await self.message.send_message(sg.HOST, mt.FOOTER, html=footer)

    async def send_content(self, received_param:str, disconnecting=False):
        status = await self.Room.get_live_room_status()
        if status == rs.ANSWER:
            await self._send_content(received_param, disconnecting)

class CQuestionPreviewState(CContent):
    def __init__(self, parent, Room, Room_member, Message, *args, **kwargs):
        super().__init__(parent, Room, Room_member, Message, *args, **kwargs)

        self.DEBUG = False
        self.template_folder += "/question_preview"

    @database_sync_to_async
    def _create_body(self) -> tuple:
        """
        Must be called with await. \n
        Renders dynamic webpage body content, depending on messager_content parameter

        :param message_content: mc.WAITING_ROOM or mc.QUESTION to define content
        :param user_type: mc.ALL, ut.MEMBER, ut.HOST to define content
        :return: when called asyncronously, content string to be sent via websocket to webpage
        """

        room_members = QuizRoomMember.objects.filter(room=self.Room.room).exclude(nickname="Host")
        joker_remaining_dict = {room_member.nickname: True for room_member in room_members}

        jokers_played = QuizRoomMemberAnswer.objects.filter(room=self.Room.room, joker_status=True).\
            order_by('user').\
            values(nickname=F('room_member_id__nickname')).\
            annotate(total=Count('user'))
        # jokers_played = QuizRoomMemberAnswer.objects.filter(room=self.Room.room, joker_status=True).\
        #     annotate(total=Count('joker_status')).order_by('user')

        # for room_member_answer in jokers_played:
        #     # if room_member_answer.total >= self.constants.MAX_JOKERS:
        #     if room_member_answer.total >= self.constants.MAX_JOKERS:
        #         joker_remaining_dict.pop(room_member_answer.room_member.nickname, None)

        for member in jokers_played:
            # if room_member_answer.total >= self.constants.MAX_JOKERS:
            if member.get('total', 0) >= self.constants.MAX_JOKERS:
                joker_remaining_dict.pop(member.get('nickname'), None)


        # render the content to string
        content = render_to_string(f"{self.template_folder}/body.html", {
            'question': self.Room.room.current_question,
            'score_multiplier': str(self.Room.room.current_question.score_multiplier.normalize()),
            'time_limit': self.constants.PREVIEW_TIMEOUT
        })

        return content, json.dumps(joker_remaining_dict)

    @database_sync_to_async
    def _create_footer_host(self, button_text) -> None:
        """
        Must be called with await. \n
        Renders dynamic webpage body content, depending on messager_content parameter

        :param message_content: mc.WAITING_ROOM or mc.QUESTION to define content
        :param user_type: mc.ALL, ut.MEMBER, ut.HOST to define content
        :return: when called asyncronously, content string to be sent via websocket to webpage
        """

        content = render_to_string(f"{self.template_folder}/footer_host.html", {
            'button_text': button_text,
            'room': self.Room.room
        })
        return content

    async def _create_header(self) -> None:
        """
        Must be called with await. \n
        Renders dynamic webpage header content, depending on messager_content and user_type parameters

        :param message_content: mc.WAITING_ROOM or mc.QUESTION to define content
        :param user_type: ut.ALL, ut.MEMBER or ut.HOST
        :return: whem called asyncronously, content string to be sent via websocket to webpage
        """
        question_number = await self.Room.get_current_question_number()
        last_question_number = await self.Room.get_last_question_number()
        content = render_to_string(f"{self.template_folder}/header.html", {
            'question_number': question_number,
            'last_question_number': last_question_number
        })

        return content

    async def _send_content(self, received_param:str, disconnecting:bool =False) -> None:
        if self.Room.user_is_host:
            header = await self._create_header()
            await self.message.send_message(sg.ALL, mt.HEADER, html=header)

            footer = await self._create_footer_host("")
            await self.message.send_message(sg.ME, mt.FOOTER, html=footer)

            body, data = await self._create_body()
            await self.message.send_message(sg.ALL, mt.PREVIEW_STATE_SCRIPT, html=body, data=data, animation=at.HORIZONTAL_GROW)
        else:
            if disconnecting == False:
                header = await self._create_header()
                await self.message.send_message(sg.ME, mt.HEADER, html=header)

                body, data = await self._create_body()
                await self.message.send_message(sg.ME, mt.PREVIEW_STATE_SCRIPT, html=body, data=data, animation=at.HORIZONTAL_GROW)

    async def send_content(self, received_param:str, disconnecting=False):
        status = await self.Room.get_live_room_status()
        if status == rs.QUESTION_PREVIEW:
            await self._send_content(received_param, disconnecting)

class CQuestionState(CContent):
    def __init__(self, parent, Room, Room_member, Message, *args, **kwargs):
        super().__init__(parent, Room, Room_member, Message, *args, **kwargs)

        self.DEBUG = False
        self.template_folder += "/question"
        self.di = di()

    @database_sync_to_async
    def _create_body(self, user_type) -> tuple:
        """
        Must be called with await. \n
        Renders dynamic webpage body content, depending on messager_content parameter

        :param message_content: mc.WAITING_ROOM or mc.QUESTION to define content
        :param user_type: mc.ALL, ut.MEMBER, ut.HOST to define content
        :return: when called asyncronously, content string to be sent via websocket to webpage
        """

        # get all answers for the current question and convert to list as template language cannot
        # access database fields aynchronously
        # answers = Answer.objects.filter(question = self.Room.room.current_question).all()
        # answer_list = [{
        #     "answer": answer.answer,
        #     "answer_number": answer.answer_number,
        #     "answer_colour": self.colours.get(answer.answer_number, '#7f7f7f')
        # }
        #     for answer in answers]

        question = Question.objects.get(pk=self.Room.room.current_question.id)
        answer_list = []
        longest_answer = 0
        for i, answer in enumerate(['answer_1', 'answer_2', 'answer_3', 'answer_4']):
            answer_text = getattr(question, answer)
            if answer_text is None or len(answer_text) == 0:
                continue
            if len(answer_text) > longest_answer:
                longest_answer = len(answer_text)
            answer_list.append(
                {"answer": answer_text, "answer_number": i + 1,
                 "answer_colour": self.colours.get(i + 1)}
            )

        answer_text_size = fn.get_text_size(longest_answer)

        # disable the answer buttons if member has already answered or current user is host
        # disable_buttons = ""
        # if user_type == ut.HOST:
        #     disable_buttons = "disabled"
        # else:
        #     room_member_answer = QuizRoomMemberAnswer.objects.get_or_none(
        #         room=self.Room.room, user=self.User.user)
        #     if room_member_answer is not None:
        #         disable_buttons = "disabled"
        host = False
        if user_type == ut.HOST:
            host=True

        if isEmpty(question.media_url):
            if isEmpty(question.default_image_number):
                media_url = self.di.get_default_image_url(self.di.get_random_default_image_number())
            else:
                media_url = self.di.get_default_image_url(question.default_image_number)
            # media_url = default_images[random.randint(0, len(default_images)-1)]
            # question.media_url = media_url
            # question.save()
        elif question.media_url.startswith('http'):
            media_url = question.media_url
        else:
            media_url = f"{settings.APP_ROOT_URL}{settings.MEDIA_URL}{question.quiz.id}/{question.media_url}"

        # answers_expected = \
        #     QuizRoomMember.objects.filter(room=self.Room.room, status__description=rms.JOINED).count() - 1

        answers_expected = self.Room_member.get_members_count_sync(status = rms.JOINED) - 1
        # answer_count = QuizRoomMemberAnswer.objects.filter(
        #     room=self.Room.room, question=self.Room.room.current_question).count()
        answer_count = self.Room_member.get_answers_count_sync()
        time_remaining = self.Room.get_time_remaining()
        if question.transition_type is not None:
            transition_function = question.transition_type.function
        else:
            transition_function = at.HORIZONTAL_GROW

        # render the content to string
        html = render_to_string(f"{self.template_folder}/body.html", {
            'question': self.Room.room.current_question,
            'media_url': media_url,
            'answers': answer_list,
            'answer_status': f"{answer_count}/{answers_expected}",
            'answer_text_size': answer_text_size,
            'time_limit': time_remaining,
            'host': host
        })

        return html, transition_function

    async def _create_header(self) -> None:
        """
        Must be called with await. \n
        Renders dynamic webpage header content, depending on messager_content and user_type parameters

        :param message_content: mc.WAITING_ROOM or mc.QUESTION to define content
        :param user_type: ut.ALL, ut.MEMBER or ut.HOST
        :return: whem called asyncronously, content string to be sent via websocket to webpage
        """
        question_number = await self.Room.get_current_question_number()
        # answers_expected = await self.Room_member.get_members_count(status = rms.JOINED) - 1
        # answer_count = await self.Room_member.get_answers_count()
        # time_remaining = await self.Room.get_time_remaining()
        content = render_to_string(f"{self.template_folder}/header.html", {
            'question_number': question_number
            # 'answer_status': f"{answer_count}/{answers_expected}",
            # 'time_limit': time_remaining
        })

        return content

    async def _send_content(self, received_param:str, disconnecting:bool =False) -> None:
        if self.DEBUG:
            print (f"{self.Room.room.user.username} sending question state messages")
        if self.Room.user_is_host:
            header = await self._create_header()
            await self.message.send_message(sg.ALL, mt.HEADER, html=header)

            body, transition_function = await self._create_body(ut.HOST)
            await self.message.send_message(sg.ME, mt.BODY, html=body, animation=transition_function)

            body, transition_function = await self._create_body(ut.MEMBER)
            await self.message.send_message(sg.MEMBER, mt.BODY, html=body, animation=transition_function)
        else:
            if disconnecting == False:
                header = await self._create_header()
                await self.message.send_message(sg.ME, mt.HEADER, html=header)

                body, transition_function = await self._create_body(ut.MEMBER)
                await self.message.send_message(sg.ME, mt.BODY, html=body, animation=transition_function)

    async def send_content(self, received_param:str, disconnecting=False):
        status = await self.Room.get_live_room_status()
        if status == rs.QUESTION:
            await self._send_content(received_param, disconnecting)

class CRestartState(CContent):
    def __init__(self, parent, Room, Room_member, Message, *args, **kwargs):
        super().__init__(parent, Room, Room_member, Message, *args, **kwargs)

        self.DEBUG = False
        self.template_folder += "/restart"

    @database_sync_to_async
    def _create_body(self) -> str:
        """
        Must be called with await. \n
        Renders dynamic webpage body content, depending on messager_content parameter

        :param message_content: mc.WAITING_ROOM or mc.QUESTION to define content
        :param user_type: mc.ALL, ut.MEMBER, ut.HOST to define content
        :return: when called asyncronously, content string to be sent via websocket to webpage
        """

        questions = Question.objects.filter(
            quiz = self.Room.room.quiz, question_number__lte=self.Room.room.current_question.question_number).all()
        content = render_to_string(f"{self.template_folder}/body_host.html", {
            'questions': questions
        })
        return content

    @database_sync_to_async
    def _create_footer_host(self) -> str:
        """
        Must be called with await. \n
        Renders dynamic webpage body content, depending on messager_content parameter

        :param message_content: mc.WAITING_ROOM or mc.QUESTION to define content
        :param user_type: mc.ALL, ut.MEMBER, ut.HOST to define content
        :return: when called asyncronously, content string to be sent via websocket to webpage
        """

        # questions = Question.objects.filter(quiz=self.Room.room.quiz)

        content = render_to_string(f"{self.template_folder}/footer_host.html", {
        })
        return content

    @database_sync_to_async
    def _create_header(self, user_type) -> None:
        """
        Must be called with await. \n
        Renders dynamic webpage header content, depending on messager_content and user_type parameters

        :param message_content: mc.WAITING_ROOM or mc.QUESTION to define content
        :param user_type: ut.ALL, ut.MEMBER or ut.HOST
        :return: whem called asyncronously, content string to be sent via websocket to webpage
        """
        content = render_to_string(f"{self.template_folder}/header_host.html", {
            'room': self.Room.room,
            'user_type': user_type
        })

        return content

    async def _send_content(self, received_param:str, disconnecting:bool =False) -> None:
        """
        Must be called using await. \n
        Note: this method should not be called directly, it should be called via the send_messages
        method of self.room. Calling this routing directly could result in messages being sent for
        a stale room state \n
        Format and send websocket messages

        :param disconnecting: indicates the message generator whether the user is in the rocessing of a websocket disconnect
        :return: if called using await: None
        """
        if self.DEBUG:
            print (f"{self.Room.user.username} restart state messages")
        if self.Room.user_is_host:
            if disconnecting:
                # host is disconnecting - send header and body to members
                header = await self._create_header(ut.HOST)
                await self.message.send_message(sg.ME, mt.HEADER, html=header)

                body = await self._create_body()
                await self.message.send_message(sg.ME, mt.BODY, html=body)
            else:
                # host is not disconnecting - send headers and body to everyone
                header = await self._create_header(ut.HOST)
                await self.message.send_message(sg.ME, mt.HEADER, html=header)

                footer = await self._create_footer_host()
                await self.message.send_message(sg.ME, mt.FOOTER, html=footer)

                body = await self._create_body()
                await self.message.send_message(sg.ME, mt.BODY, html=body)

    async def send_content(self, received_param:str, disconnecting=False):
        status = await self.Room.get_live_room_status()
        if status == rs.WAITING:
            await self._send_content(received_param, disconnecting)

class CResultsState(CContent):
    def __init__(self, parent, Room, Room_member, Message, *args, **kwargs):
        super().__init__(parent, Room, Room_member, Message, *args, **kwargs)

        self.DEBUG = False
        self.template_folder += "/results"

    @database_sync_to_async
    def _create_body(self, user_type) -> tuple:
        """
        Must be called with await. \n
        Renders dynamic webpage body content, depending on messager_content parameter
        :param message_content: mc.WAITING_ROOM or mc.QUESTION to define content
        :param user_type: mc.ALL, ut.MEMBER, ut.HOST to define content
        :return: when called asyncronously, content string to be sent via websocket to webpage
        """
        leader_dict = {}
        old_leaderboard = []
        new_leaderboard = []
        leaderboard_length = c.LEADERBOARD_SIZE_MAX
        # get leaderboard after previous question
        old_leaders = QuizRoomMemberAnswer.objects.filter(
            room=self.Room.room, question=self.Room.room.current_question).\
            order_by('-running_score_prior', 'room_member__nickname')[0:leaderboard_length]
        # get leaderboard after current question
        new_leaders = QuizRoomMemberAnswer.objects.filter(
            room=self.Room.room, question=self.Room.room.current_question). \
            order_by('-running_score', 'room_member__nickname')[0:leaderboard_length]

        # put old leaders in dict and list
        for i, leader in enumerate(old_leaders):
            leader_dict[leader.room_member.nickname] = {
                "nickname": leader.room_member.nickname,
                "prior_score": leader.running_score_prior,
                "points_added": leader.answer_score,
                "running_score": leader.running_score,
                "old_position": i,
                "joker": leader.joker_status
            }
            old_leaderboard.append(leader.room_member.nickname)

        # update dict with new leaders and create list
        for i, leader in enumerate(new_leaders):
            if leader.room_member.nickname not in leader_dict:
                leader_dict[leader.room_member.nickname] = {
                    "nickname": leader.room_member.nickname,
                    "prior_score": leader.running_score_prior,
                    "points_added": leader.answer_score,
                    "running_score": leader.running_score,
                    "new_position": i,
                    "joker": leader.joker_status
                }
            else:
                leader_dict[leader.room_member.nickname]["new_position"] = i
            new_leaderboard.append(leader.room_member.nickname)

        # add any leaders in new leaderboard who were not in the old_leaderboard
        i = len(old_leaderboard)
        for leader in new_leaders:
            if leader.room_member.nickname not in old_leaderboard:
                old_leaderboard.append(leader.room_member.nickname)
                leader_dict[leader.room_member.nickname]["old_position"] = i
                i += 1

        # add any leaders in old leaderboard who are not in the new leaderboard
        i = len(new_leaderboard)
        for leader in old_leaders:
            if leader.room_member.nickname not in new_leaderboard:
                new_leaderboard.append(leader.room_member.nickname)
                leader_dict[leader.room_member.nickname]["new_position"] = i
                i += 1

        html = render_to_string(f"{self.template_folder}/body.html", {
            "rows": new_leaderboard,
            "room": self.Room.room
        })

        return html, json.dumps({"leader_data": list(leader_dict.values()), "leaderboard_length": leaderboard_length})

    @database_sync_to_async
    def _create_footer_host(self) -> str:
        """
        Must be called with await. \n
        Renders dynamic webpage body content, depending on messager_content parameter

        :param message_content: mc.WAITING_ROOM or mc.QUESTION to define content
        :param user_type: mc.ALL, ut.MEMBER, ut.HOST to define content
        :return: when called asyncronously, content string to be sent via websocket to webpage
        """

        html = render_to_string(f"{self.template_folder}/footer_host.html", {
            'room': self.Room.room
        })
        return html

    @database_sync_to_async
    def _create_header(self) -> None:
        """
        Must be called with await. \n
        Renders dynamic webpage header content, depending on messager_content and user_type parameters

        :param message_content: mc.WAITING_ROOM or mc.QUESTION to define content
        :param user_type: ut.ALL, ut.MEMBER or ut.HOST
        :return: whem called asyncronously, content string to be sent via websocket to webpage
        """
        html = render_to_string(f"{self.template_folder}/header.html", {
        })

        return html

    async def _send_content(self, received_param:str, disconnecting:bool =False) -> None:
        if self.DEBUG:
            print (f"{self.Room.user.username} sending results state messages")

        html = await self._create_header()
        await self.message.send_message(sg.ALL, mt.HEADER, html=html)

        html, data = await self._create_body(ut.HOST)
        await self.message.send_message(sg.ALL, mt.RESULTS_SCRIPT, html=html, data=data, animation=at.NONE)

        footer = await self._create_footer_host()
        await self.message.send_message(sg.HOST, mt.FOOTER, html=footer)

    async def send_content(self, received_param:str, disconnecting=False):
        status = await self.Room.get_live_room_status()
        if status == rs.RESULTS:
            await self._send_content(received_param, disconnecting)

class CReturnToAnswersState(CContent):
    def __init__(self, parent, Room, Room_member, Message, *args, **kwargs):
        super().__init__(parent, Room, Room_member, Message, *args, **kwargs)

        self.DEBUG = False
        self.template_folder += "/amend_answer"
        self.di = di()

    @database_sync_to_async
    def _create_body_host(self, received_param) -> dict[str, str]:
        """
        Must be called with await. \n
        Renders dynamic webpage body content, depending on messager_content parameter

        :param message_content: mc.WAITING_ROOM or mc.QUESTION to define content
        :param user_type: mc.ALL, ut.MEMBER, ut.HOST to define content
        :return: when called asyncronously, content string to be sent via websocket to webpage
        """

        error = {}
        answer_list = ["correct_answer_1", "correct_answer_2", "correct_answer_3", "correct_answer_4"]
        correct_answer_found = False
        if type(received_param) is not dict:
            error['error'] = "Invalid entry received"
        valid_answers = [True, False]
        for answer in received_param:
            if answer not in answer_list:
                error['error'] = "Invalid entry received"
            if received_param.get(answer) not in valid_answers:
                error['error'] = "Invalid entry received"
            else:
                if received_param.get(answer) == True:
                    correct_answer_found = True

        if not correct_answer_found:
            error['error'] = "At least one correct answer must be entered"

        return error

    async def _send_content(self, received_param:str, disconnecting:bool =False) -> None:
        if self.DEBUG:
            print (f"{self.Room.room.user.username} amend answer state messages")
        if self.Room.user_is_host:
            error = await self._create_body_host(received_param)
            if len(error) > 0:
                await self.message.send_message(sg.HOST, mt.AMEND_ANSWERS_SCRIPT, html=None, data=error)

        return error

    async def send_content(self, received_param:str, disconnecting=False):
        status = await self.Room.get_live_room_status()
        if status == rs.ANSWER:
            error = await self._send_content(received_param, disconnecting)
            return error

        return None

class CScoreMultiplierState(CContent):
    def __init__(self, parent, Room, Room_member, Message, *args, **kwargs):
        super().__init__(parent, Room, Room_member, Message, *args, **kwargs)

        self.DEBUG = False
        self.template_folder += "/score_multiplier"

    @database_sync_to_async
    def _create_body(self) -> str:
        """
        Must be called with await. \n
        Renders dynamic webpage body content, depending on messager_content parameter

        :param message_content: mc.WAITING_ROOM or mc.QUESTION to define content
        :param user_type: mc.ALL, ut.MEMBER, ut.HOST to define content
        :return: when called asyncronously, content string to be sent via websocket to webpage
        """

        # render the content to string
        content = render_to_string(f"{self.template_folder}/body.html", {
            'question': self.Room.room.current_question,
            'score_multiplier': str(self.Room.room.current_question.score_multiplier.normalize())
        })

        return content

    @database_sync_to_async
    def _create_footer_host(self, button_text) -> None:
        """
        Must be called with await. \n
        Renders dynamic webpage body content, depending on messager_content parameter

        :param message_content: mc.WAITING_ROOM or mc.QUESTION to define content
        :param user_type: mc.ALL, ut.MEMBER, ut.HOST to define content
        :return: when called asyncronously, content string to be sent via websocket to webpage
        """

        content = render_to_string(f"{self.template_folder}/footer_host.html", {
            'button_text': button_text,
            'room': self.Room.room
        })
        return content

    async def _create_header(self) -> None:
        """
        Must be called with await. \n
        Renders dynamic webpage header content, depending on messager_content and user_type parameters

        :param message_content: mc.WAITING_ROOM or mc.QUESTION to define content
        :param user_type: ut.ALL, ut.MEMBER or ut.HOST
        :return: whem called asyncronously, content string to be sent via websocket to webpage
        """
        question_number = await self.Room.get_current_question_number()
        last_question_number = await self.Room.get_last_question_number()
        content = render_to_string(f"{self.template_folder}/header.html", {
            'question_number': question_number,
            'last_question_number': last_question_number
        })

        return content

    async def _send_content(self, received_param:str, disconnecting:bool =False) -> None:
        if self.Room.user_is_host:
            header = await self._create_header()
            await self.message.send_message(sg.ALL, mt.HEADER, html=header)

            footer = await self._create_footer_host("")
            await self.message.send_message(sg.ME, mt.FOOTER, html=footer)

            body= await self._create_body()
            await self.message.send_message(sg.ALL, mt.SCORE_MULTI_SCRIPT, html=body, animation=at.HORIZONTAL_GROW)
        # else:
        #     if disconnecting == False:
        #         header = await self._create_header()
        #         await self.message.send_message(sg.ME, mt.HEADER, html=header)
        #
        #         body = await self._create_body()
        #         await self.message.send_message(sg.ME, mt.BODY, html=body, animation=at.HORIZONTAL_GROW)

    async def send_content(self, received_param:str, disconnecting=False):
        status = await self.Room.get_live_room_status()
        if status == rs.SCORE_MULTIPLIER:
            await self._send_content(received_param, disconnecting)

class CWaitingState(CContent):
    def __init__(self, parent, Room, Room_member, Message, *args, **kwargs):
        super().__init__(parent, Room, Room_member, Message, *args, **kwargs)

        self.DEBUG = False
        self.template_folder += "/waiting"

    @database_sync_to_async
    def _create_body(self) -> str:
        """
        Must be called with await. \n
        Renders dynamic webpage body content, depending on messager_content parameter

        :param message_content: mc.WAITING_ROOM or mc.QUESTION to define content
        :param user_type: mc.ALL, ut.MEMBER, ut.HOST to define content
        :return: when called asyncronously, content string to be sent via websocket to webpage
        """

        members = QuizRoomMember.objects.filter(room = self.Room.room).all()
        content = render_to_string(f"{self.template_folder}/body.html", {
            'members': members
        })
        return content

    @database_sync_to_async
    def _create_footer_host(self) -> str:
        """
        Must be called with await. \n
        Renders dynamic webpage body content, depending on messager_content parameter

        :param message_content: mc.WAITING_ROOM or mc.QUESTION to define content
        :param user_type: mc.ALL, ut.MEMBER, ut.HOST to define content
        :return: when called asyncronously, content string to be sent via websocket to webpage
        """

        # questions = Question.objects.filter(quiz=self.Room.room.quiz)

        hide_restart = False
        if self.Room.room.current_question.question_number == 1:
            hide_restart = True

        content = render_to_string(f"{self.template_folder}/footer_host.html", {
            "hide_restart": hide_restart
        })
        return content

    @database_sync_to_async
    def _create_header(self, user_type) -> None:
        """
        Must be called with await. \n
        Renders dynamic webpage header content, depending on messager_content and user_type parameters

        :param message_content: mc.WAITING_ROOM or mc.QUESTION to define content
        :param user_type: ut.ALL, ut.MEMBER or ut.HOST
        :return: whem called asyncronously, content string to be sent via websocket to webpage
        """
        content = render_to_string(f"{self.template_folder}/header.html", {
            'room': self.Room.room,
            'user_type': user_type
        })

        return content

    async def _send_content(self, disconnecting:bool =False) -> None:
        """
        Must be called using await. \n
        Note: this method should not be called directly, it should be called via the send_messages
        method of self.room. Calling this routing directly could result in messages being sent for
        a stale room state \n
        Format and send websocket messages

        :param disconnecting: indicates the message generator whether the user is in the rocessing of a websocket disconnect
        :return: if called using await: None
        """
        if self.DEBUG:
            print (f"{self.Room.user.username} sending waiting state messages")
        if self.Room.user_is_host:
            if disconnecting:
                # host is disconnecting - send header and body to members
                header = await self._create_header(ut.MEMBER)
                await self.message.send_message(sg.MEMBER, mt.HEADER, html=header)

                body = await self._create_body()
                await self.message.send_message(sg.MEMBER, mt.BODY, html=body)
            else:
                # host is not disconnecting - send headers and body to everyone
                header = await self._create_header(ut.HOST)
                await self.message.send_message(sg.ME, mt.HEADER, html=header)

                footer = await self._create_footer_host()
                await self.message.send_message(sg.ME, mt.FOOTER, html=footer)

                header = await self._create_header(ut.MEMBER)
                await self.message.send_message(sg.MEMBER, mt.HEADER, html=header)

                body = await self._create_body()
                await self.message.send_message(sg.ALL, mt.BODY, html=body)
        else:
            if not disconnecting:
                header = await self._create_header(ut.MEMBER)
                await self.message.send_message(sg.ME, mt.HEADER, html=header)

            body = await self._create_body()
            await self.message.send_message(sg.ALL, mt.BODY, html=body)

    async def send_content(self, disconnecting=False):
        status = await self.Room.get_live_room_status()
        if status == rs.WAITING:
            await self._send_content(disconnecting)