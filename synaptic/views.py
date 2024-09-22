from django.contrib.auth import authenticate, login, logout
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.contrib.auth import forms as auth_forms
from django.utils.http import url_has_allowed_host_and_scheme
from django.shortcuts import render, reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.db import IntegrityError
from django.utils.translation import gettext_lazy as _
# from crispy_forms.helper import FormHelper
from .models import User, UserExtension, Quiz, QuizRoom, Question, RoomStatus
from .models import QuizRoomMember
from .forms import JoinRoomForm, UploadFilesForm, ListQuizFormSet
from .forms import QuestionForm, ListQuestionForm, BaseListQuizFormSet
from .functions import add_custom_non_field_alert, is_ajax
import json

from .functions import get_session_quiz, compose_custom_errors, compose_formset_custom_errors, is_ajax
from .functions import get_icon_buttons
from .constants import RoomStatus as rs, FormFunction as ff, MessageTypes as mt

DisplayMoneyAttrs = {'class': 'integer', "maxlength": "8"}
DisplayPercentAttrs = {'disabled': True, 'class': 'bg-white percent'}

app="synaptic"

class PasswordResetView(auth_views.PasswordResetView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Reset Password"
        context['show_navbar'] = True
        return context
    
class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Reset Password"
        context['show_navbar'] = True
        return context
    
class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Reset Password"
        context['show_navbar'] = True
        return context
    
class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Reset Password"
        context['show_navbar'] = True
        return context
    
def index(request):
    if not 'message' in request.session:
        request.session['message'] = {"message": "", "message_type": mt.SUCCESS}
    icon_buttons = get_icon_buttons(save=False, cancel=False, back=False)

    message = request.session['message']
    request.session['message'] = {"message": "", "message_type": mt.SUCCESS}
    return render(request, f"{app}/index.html", {
        "title": "Synaptic",
        "show_navbar": True,
        "icon_buttons": icon_buttons,
        "message": message
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            redirect = request.POST.get('next')
            if redirect == None:
                return HttpResponseRedirect(reverse("synaptic:index"))
            else:
                if url_has_allowed_host_and_scheme(redirect, allowed_hosts=request.get_host()):
                    return HttpResponseRedirect(redirect)
                else:
                    return HttpResponseRedirect(reverse(f"{app}:index"))
        else:
            return render(request, f"{app}/login.html", {
                "message": "Invalid username and/or password.",
                "title": "Login",
                "show_navbar": True,
            })
    else:
        return render(request, f"{app}/login.html", {
            "title": "Login",
            "show_navbar": True,
        })
    
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse(f"{app}:index"))

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, f"{app}/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, f"{app}/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse(f"{app}:index"))
    else:
        return render(request, f"{app}/register.html")
    
@login_required
def add_quiz_view(request):
    request.session["quiz_pk"] = None
    request.session['quiz_function'] = ff.CREATE
    return HttpResponseRedirect(reverse(f"{app}:quiz"))

@login_required
def join_room_view(request):
    if request.method == "POST":
        form = JoinRoomForm(data=request.POST, request=request)
        if form.is_valid():
            user = User.objects.get(username=request.user)
            form.save_room_member(form, user)
            return HttpResponseRedirect(reverse(f"{app}:live_room", args=[form.cleaned_data["room_number"]]))
        member_rooms = form.get_room_member(request)
        return render (request, f"{app}/join_room.html", {
            "form": form,
            "title": "Join Room",
            "initial_menu_state": "",
            "room_members": member_rooms
        })

    form = JoinRoomForm()
    member_rooms = form.get_room_member(request)
    return render (request, f"{app}/join_room.html", {
        "form": form,
        "title": "Join Room",
        "initial_menu_state": "",
        "room_members": member_rooms
    })

@login_required
def live_room_view(request, room_number):
    room = QuizRoom.objects.get_or_none(room_number=room_number)
    if room == None:
        return HttpResponseRedirect(reverse(f"{app}:join_room"))
    user = User.objects.get(username=request.user)
    room_member = QuizRoomMember.objects.filter(room=room, user=user).all()
    if room.status.description != rs.WAITING and len(room_member) == 0:
        return HttpResponseRedirect(reverse(f"{app}:join_room"))
    quiz = Quiz.objects.get(pk=room.quiz_id)
    template = f"{app}/live_room.html"
    title = "Live Room Preview"
    if room.host.username == request.user.username:
        template = f"{app}/live_room_host.html"
        title = "Live Room"
    return render(request, template, {
        "quiz": quiz,
        "room": room,
        "title": title,
        "show_header": "",
        "question_number": "",
        "show_navbar": False,
        "nickname": room_member[0].nickname
    })

@login_required
def list_questions_view(request, action=None):
    if not 'message' in request.session:
        request.session['message'] = {"message": "", "message_type": mt.SUCCESS}
    if request.method == "POST" and is_ajax(request):
        resp = {}
        resp['success'] = False
        resp = ListQuestionForm.validate_button(request, resp)
        if 'errors' in resp:
            return HttpResponse(json.dumps(resp), content_type="application/json")

        button = request.POST['submit']
        if button == "Cancel":
            resp = ListQuestionForm.process_cancel_button(resp)
            return HttpResponse(json.dumps(resp), content_type="application/json")

        list_question_form, quiz = ListQuestionForm.validate_and_save(request, resp)
        if 'errors' in resp:
            return HttpResponse(json.dumps(resp), content_type="application/json")

        if button == "Add":
            resp = ListQuestionForm.process_add_button(request, resp)
            return HttpResponse(json.dumps(resp), content_type="application/json")

        if button == "Back":
            resp = ListQuestionForm.process_back_button(resp)
            return HttpResponse(json.dumps(resp), content_type="application/json")

        if button == "Preview":
            ListQuestionForm.process_preview_button(request, resp)
            return HttpResponse(json.dumps(resp), content_type="application/json")

        if button == "Update":
            ListQuestionForm.process_update_button(request, request.session['resp'])
            return HttpResponse(json.dumps(request.session['resp']), content_type="application/json")

        resp = list_question_form.get_update_preview_redirect(request, quiz)
        if 'errors' in resp:
            return HttpResponse(json.dumps(resp), content_type="application/json")

        resp['success'] = True
        resp['redirect'] = reverse("synaptic:list_questions")
        return HttpResponse(json.dumps(resp), content_type="application/json")

    # request method is GET
    quiz_pk = request.session.get('quiz_pk')
    if quiz_pk == None:
        return HttpResponseRedirect(reverse(f"{app}:list_quizzes"))
    # need to check for None returned
    quiz = Quiz.objects.get_or_none(pk=quiz_pk)
    questions = Question.objects.filter(quiz = quiz).all()
    message = request.session['message']
    request.session['message'] = {"message": "", "message_type": mt.SUCCESS}
    icon_buttons = get_icon_buttons(
        add=True, add_button_state="enabled", expand=True, expand_button_state="enabled"
    )
    return render(request, f"{app}/list_questions.html", {
        "questions": questions,
        "quiz": quiz,
        "title": "Quiz Questions",
        "heading": f"Quiz Questions for {quiz.title}",
        "action": action,
        "message": message,
        "show_navbar": False,
        "icon_buttons": icon_buttons
    })

@login_required
def list_quizzes_view(request):
    if not 'message' in request.session:
        request.session['message'] = {"message": "", "message_type": mt.SUCCESS}
    if request.method == "POST" and is_ajax(request):
        request.session['resp'] = {}
        if request.POST['submit'] == "Cancel":
            BaseListQuizFormSet.process_cancel(request.session['resp'])
            return HttpResponse(json.dumps(request.session['resp']), content_type="application/json")
        formset = BaseListQuizFormSet.get_formset(request)
        if formset is None:
            return HttpResponseRedirect(reverse(f"{app}:list_quizzes"))

        if formset.is_valid():
            formset.save_changes(request, request.session['resp'])
            formset.process_button(request, request.session['resp'])
            request.session['resp']['success'] = True
        else:
            compose_formset_custom_errors(formset, request.session['resp'])
            request.session['resp']['success'] = False
        return HttpResponse(json.dumps(request.session['resp']), content_type="application/json")

    formset = ListQuizFormSet(
        queryset=Quiz.objects.filter(created_by = request.user).order_by('-created_date')
    )
    # request method is GET (or POST and not ajax)
    message = request.session['message']
    request.session['message'] = {"message": "", "message_type": mt.SUCCESS}
    icon_buttons = get_icon_buttons(add=True, add_button_state="enabled")
    return render(request, f'{app}/list_quizzes.html', {
        'formset': formset,
        "title": "Manage Quizzes",
        "heading": "My Quizzes",
        "message": message,
        "show_navbar": False,
        "action": "manage",
        "icon_buttons": icon_buttons
    })

@login_required
def list_quizzes_view(request):
    if not 'message' in request.session:
        request.session['message'] = {"message": "", "message_type": mt.SUCCESS}
    if request.method == "POST" and is_ajax(request):
        request.session['resp'] = {}
        if request.POST['submit'] == "Cancel":
            BaseListQuizFormSet.process_cancel(request.session['resp'])
            return HttpResponse(json.dumps(request.session['resp']), content_type="application/json")
        formset = BaseListQuizFormSet.get_formset(request)
        if formset is None:
            return HttpResponseRedirect(reverse(f"{app}:list_quizzes"))

        if formset.is_valid():
            formset.save_changes(request, request.session['resp'])
            formset.process_button(request, request.session['resp'])
            request.session['resp']['success'] = True
        else:
            compose_formset_custom_errors(formset, request.session['resp'])
            request.session['resp']['success'] = False
        return HttpResponse(json.dumps(request.session['resp']), content_type="application/json")

    formset = ListQuizFormSet(
        queryset=Quiz.objects.filter(created_by = request.user).order_by('-created_date')
    )
    # request method is GET (or POST and not ajax)
    message = request.session['message']
    request.session['message'] = {"message": "", "message_type": mt.SUCCESS}
    icon_buttons = get_icon_buttons(add=True, add_button_state="enabled")
    return render(request, f'{app}/list_quizzes.html', {
        'formset': formset,
        "title": "Manage Quizzes",
        "heading": "My Quizzes",
        "message": message,
        "show_navbar": False,
        "action": "manage",
        "icon_buttons": icon_buttons
    })

@login_required
def question_view(request):
    quiz_pk, quiz = get_session_quiz(request)
    if quiz is None:
        return HttpResponseRedirect(reverse(f"{app}:list_questions"))
    question_action = request.session.get("question_action")
    if question_action is None:
        return HttpResponseRedirect(reverse(f"{app}:list_questions"))

    if not 'message' in request.session:
        request.session['message'] = {"message": "", "message_type": mt.SUCCESS}

    if request.method == "POST"  and is_ajax(request):
        resp = {}
        #request.session['message'] = {"message": "", "message_type": mt.SUCCESS}
        if request.POST['submit'] == "Cancel":
            QuestionForm.process_cancel_button(resp)
            return HttpResponse(json.dumps(resp), content_type="application/json")

        resp = QuestionForm.validate_button(request, resp)
        if resp.get('errors'):
            return HttpResponse(json.dumps(resp), content_type="application/json")

        initial_values = None
        question = Question.objects.get_or_none(
            quiz=quiz, question_number = request.session["question_number"])
        form = QuestionForm(data=request.POST, request=request, instance=question)
        if form.is_valid():
            form.save_question(quiz, question, request, resp)
            resp['success'] = True

            if request.POST['submit'] == "Back":
                form.process_back_button(resp)
                return HttpResponse(json.dumps(resp), content_type="application/json")

            if request.POST['submit'] == "Prev":
                form.process_prev_button(request, resp)
                return HttpResponse(json.dumps(resp), content_type="application/json")

            if request.POST['submit'] == "Next":
                form.process_next_button(quiz, request, resp)
                return HttpResponse(json.dumps(resp), content_type="application/json")

            if request.POST['submit'] == "Add":
                form.process_add_button(quiz, request, resp)
                return HttpResponse(json.dumps(resp), content_type="application/json")

            if request.POST['submit'] == "Save":
                form.process_save_button(request, resp)
                return HttpResponse(json.dumps(resp), content_type="application/json")

            resp['redirect'] = reverse(f"{app}:question")
        else:
            resp = compose_custom_errors(form, resp)
            resp['success'] = False

        return HttpResponse(json.dumps(resp), content_type="application/json")

    # request method is GET
    if question_action == ff.CREATE:
        request, form, icon_buttons = QuestionForm.initialise_create(quiz, request)
    else:
        if request.session.get("question_number") is None:
            return HttpResponseRedirect(reverse(f"{app}:list_questions"))
        request, form, icon_buttons = QuestionForm.initialise_update(quiz, request)

    message = request.session['message']
    request.session['message'] = {"message": "", "message_type": mt.SUCCESS}
    return render (request, f"{app}/question.html", {
        "form": form,
        "title": f"{question_action.title()} Question: {request.session['question_number']} for {quiz.title}",
        "message": message,
        "icon_buttons": icon_buttons

    })

@login_required
def upload_quiz_spreadsheet_view(request):
    quiz_pk = request.session.get('quiz_pk', None)
    if quiz_pk == None:
        return HttpResponseRedirect(reverse(f"{app}:list_quizzes"))
    quiz = Quiz.objects.get_or_none(pk=quiz_pk)
    if quiz == None:
        return HttpResponseRedirect(reverse(f"{app}:list_quizzes"))

    if not 'message' in request.session:
        request.session['message'] = {"message": "", "message_type": mt.SUCCESS}

    if request.method == "POST" and is_ajax(request):
        resp = {}
        button = request.POST['submit']
        if button == "Cancel":
            UploadFilesForm.process_cancel(resp)
            return HttpResponse(json.dumps(resp), content_type="application/json")

        form = UploadFilesForm(data=request.POST, request=request)
        resp = {}
        if form.is_valid():
            if button not in ['Back', 'Upload']:
                add_custom_non_field_alert(resp, "Invalid submission received")
                #resp['non_field_error'] = {'alert': "Invalid submission received"}
                return HttpResponse(json.dumps(resp), content_type="application/json")
            form.save_changes(request, resp)
            if button in ['Back']:
                resp['redirect'] = reverse(f"{app}:list_quizzes")
            if button in ['Upload']:
                resp['redirect'] = reverse(f"{app}:upload_quiz_spreadsheet")
            resp['success'] = True
        else:
            resp['success'] = False
            compose_custom_errors(form, resp)
            #resp['errors'] = form.field_custom_errors

        return HttpResponse(json.dumps(resp), content_type="application/json")

    form = UploadFilesForm()
    quiz = Quiz.objects.get_or_none(pk=quiz_pk)
    icon_buttons = get_icon_buttons(save=False, upload=True)
    message = request.session['message']
    request.session['message'] = {"message": "", "message_type": mt.SUCCESS}
    return render(request, f"{app}/upload_quiz_spreadsheet.html", {
        "form": form,
        "quiz": quiz,
        "initial_menu_state": "",
        "message": message,
        "icon_buttons": icon_buttons
    })