from .models import Quiz, Question, QuizRoom, RoomStatus, QuizRoomMember, RoomMemberStatus, CheckStatus
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db.models import Max
from django.shortcuts import reverse
from django.core.files.storage import FileSystemStorage

import openpyxl
import random
import requests
from datetime import datetime as dt
from .constants import ExcelConstants as xl, RoomStatus as rs, RoomMemberStatus as rms, CheckStatus as cs
from openpyxl.styles.numbers import is_date_format
import numbers

def add_custom_field_error(self, field, error, css_id):
    if 'field' in self.field_custom_errors:
        return
    self.field_custom_errors[css_id] = str(_(error))
    self.add_error(field, error)

def add_custom_non_field_alert(resp, message):
    resp['non_field_error'] = {'alert': str(_(message))}
    resp['errors'] = True
    return resp

def compose_formset_custom_errors(formset, resp):
    for form in formset:
        form_resp = form.non_field_custom_errors.get('resp')
        if form_resp is None:
            continue

        non_field_error = form_resp.get('non_field_error')
        if non_field_error is None:
            continue

        alert = non_field_error.get('alert')
        if alert is None:
            continue

        add_custom_non_field_alert(resp, non_field_error['alert'])
        resp['errors'] = True
        return

def compose_custom_errors(form, resp):
    if 'field_errors' not in resp:
        resp['field_errors'] = {}
    for key in form.field_custom_errors:
        resp['field_errors'] = {key: form.field_custom_errors[key]}
    for key in form.errors:
        css_id = f"#id_{key}_error"
        if css_id not in resp['field_errors']:
            resp['field_errors'][css_id] = str(form.errors[key][0])
    if 'field_errors' in resp or 'non_field_errors' in resp:
        resp['errors'] = True
    return resp

def generate_room(quiz_id, status=rs.WAITING, preview=False, first_question_number=None, last_question_number=None):
    quiz = Quiz.objects.get(pk=quiz_id)
    QuizRoom.objects.filter(host=quiz.created_by, preview=True).delete()
    if preview:
        QuizRoom.objects.filter(host=quiz.created_by, preview=True).delete()
    room = QuizRoom.objects.get_or_none(
        quiz=quiz, host=quiz.created_by, opened_date = dt.today().astimezone(), preview=preview)
    if room == None:
        room_number = generate_room_number()
        if first_question_number == None:
            first_question = Question.objects.filter(quiz=quiz).first()
        else:
            first_question = Question.objects.get_or_none(quiz=quiz, question_number=first_question_number)
        status = RoomStatus.objects.get_or_none(description=status)
        room = QuizRoom(host = quiz.created_by, quiz=quiz ,current_question=first_question,
                        status=status, room_number=room_number,
                        countdown_seconds_remaining=first_question.time_limit,
                        preview=preview)

    if last_question_number == None:
        last_question = Question.objects.filter(quiz=room.quiz).last()
    else:
        if last_question_number == first_question_number:
            last_question = first_question
        else:
            last_question = Question.objects.get_or_none(quiz=quiz, question_number=last_question_number)
    room.last_question=last_question
    room.save()
    room_member_status = RoomMemberStatus.objects.get_or_none(description=rms.LEFT)
    if QuizRoomMember.objects.filter(room=room, user=quiz.created_by).count() == 0:
        QuizRoomMember(room=room, user=quiz.created_by, status=room_member_status, nickname="Host", preview=preview).save()
    return room

def generate_room_number():
    while True:
        room_number = random.randint(10000000, 99999999)
        room = QuizRoom.objects.get_or_none(room_number=room_number)
        if room == None:
            return room_number

def get_answer_list(question, colours):
    answer_set = ['answer_1', 'answer_2', 'answer_3', 'answer_4']
    answer_status = {}
    answer_totals = {}
    answer_list = []
    longest_answer = 0
    for i, answer in enumerate(answer_set):
        answer_text = getattr(question, answer)
        if answer_text is None or len(answer_text) == 0:
            continue
        if len(answer_text) > longest_answer:
            longest_answer = len(answer_text)
        correct_answer = getattr(question, f"correct_{answer}")
        answer_list.append(
            {"answer": answer_text, "answer_number": i + 1,
             "answer_colour": colours.get(i + 1), "correct_answer": correct_answer}
        )
        answer_status[i + 1] = getattr(question, f"correct_{answer}")
        answer_totals[i + 1] = 0

    answer_text_size = get_text_size(longest_answer)
    return answer_set, answer_list, answer_status, answer_totals, answer_text_size

def get_icon_buttons (add=False, back=True, cancel=True, check=False, expand=False,
                      next=False, prev=False, save=True, upload=False,
                      add_button_text="Add New", back_button_text="Back",
                      cancel_button_text="Cancel", check_button_text = "Check",
                      expand_button_text="Show Details",
                      next_button_text="Next", prev_button_text="Previous",
                      save_button_text="Save", upload_button_text="Upload",
                      add_button_state="disabled", back_button_state="enabled",
                      cancel_button_state="disabled", check_button_state="disabled",
                      expand_button_state="disabled",
                      next_button_state="disabled", prev_button_state="disabled",
                      save_button_state="disabled", upload_button_state="disabled"
                      ):
    return {**locals()}
#
def get_last_question_number(quiz):
    last_question_number = Question.objects.filter(quiz=quiz).aggregate(Max('question_number'))
    if last_question_number is None:
        return None
    return last_question_number['question_number__max']

def get_new_question_number(request, quiz):
    # set question number for added question
    # question_number = request.session["question_number"]
    # if question_number == None:
    question_number  = 1
    if Question.objects.filter(quiz=quiz).count() > 0:
        question = Question.objects.filter(quiz=quiz).order_by('-question_number')[0]
        question_number = question.question_number + 1
    return question_number

def get_openpyxl_formatted_value(cell):
    if is_date_format(cell.number_format):
        # Convert serial number to datetime
        return dt.fromordinal(dt(1900, 1, 1).toordinal() + int(cell.value) - 2)
    elif isinstance(cell.value, numbers.Number):
        # Handling numerical values, including percentages
        return format(cell.value, cell.number_format)
    else:
        # Return value as is for strings and other types
        return cell.value

def get_session_quiz(request: object):
    """
    Get quiz_pk from request.session and return quiz_pk and associated quiz object

    :param request: request object from client get/post
    :return: quiz object primary key if found in request.session; quiz object if found, otherwise None
    """
    quiz_pk = request.session.get('quiz_pk', None)
    if quiz_pk is None:
        return None, None
    quiz = Quiz.objects.get_or_none(pk=quiz_pk)
    return quiz_pk, quiz

def get_text_size(text_length):
    if text_length > 40:
        return "text-md"
    if text_length > 20:
        return "text-lg"
    return "text-xl"

def get_url_content_type(url):
    r=requests.head(url)
    if r.status_code == 403:
        headers = {
            'User-Agent': 'Mozilla/5.0',
        }
        r = requests.head(url, headers=headers)
    content_type = ""
    content_dict = {key.lower().replace('-', '_'): r.headers[key] for key in r.headers if key.lower().startswith('content')}
    if 'content_type' in content_dict:
        content_type = content_dict['content_type']
    return content_type.lower()

def quiz_validation(quiz):
    question_errors = []
    quiz_errors = []
    questions = Question.objects.filter(quiz=quiz).all().order_by('question_number')
    if len(questions) == 0:
        quiz_errors.append("No questions added to quiz")
        return quiz_errors, question_errors
    for question in questions:
        error_msgs = []
        correct_answer = False
        if len(question.question) == 0:
            error_msgs.append('No question text')
        for answer in ['answer_1', 'answer_2', 'answer_3', 'answer_4']:
            answer_text = getattr(question, answer)
            if answer_text is not None:
                if len(answer_text) > 0 and getattr(question, f"correct_{answer}") == True:
                    correct_answer = True
        if correct_answer == False:
            error_msgs.append("No correct answers marked")
        if len(error_msgs) > 0:
            question_errors.append({
                "number": question.question_number,
                "question": question.question,
                "errors": "<br>".join(error_msgs)
            })

    return quiz_errors, question_errors

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

def isEmpty(value):
    if value is None or value == "":
        return True
    return False

def set_score_multiplier(multiplier):
    if multiplier is None:
        return 1
    if multiplier is not None:
        if multiplier < 0.1:
            return 1
        if multiplier > 10:
            return 10
    return multiplier

def set_time_limit(limit):
    if limit is None:
        return 30
    if limit < 2:
        return 30
    return limit

def get_upload_media_filenames(request, file_container_name):
    filenames = []
    if request.FILES.get(file_container_name) != None:
        for file in request.FILES.getlist(file_container_name):
            filenames.append(file.name)
    return filenames

def upload_media_files(request, quiz, file_container_name):
    fs = FileSystemStorage()
    fs.location += f"/{quiz.pk}"
    if request.FILES.get(file_container_name) != None:
        for file in request.FILES.getlist(file_container_name):
            fs.delete(file.name)
            filename = fs.save(file.name, file)