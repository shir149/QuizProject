from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ObjectDoesNotExist
from .constants import CheckStatus as cs

from datetime import date
from .validators import validate_non_past_date

class MyManager(models.Manager):
    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except ObjectDoesNotExist:
            return None

class User(AbstractUser):
    pass

class UserExtension(models.Model):
    objects=MyManager()
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True, verbose_name="User")

class TransitionType(models.Model):
    objects=MyManager()
    description = models.CharField(
        max_length=20, null=False, blank=False,
        verbose_name="Transition Type")
    function = models.CharField(
        max_length=20, null=True, blank=False,
        verbose_name="Function")

    def __str__(self):
        return f"{self.description}"

    class Meta:
        ordering = ['description']

class RoomMemberStatus(models.Model):
    objects=MyManager()
    description = models.CharField(
        max_length=20, null=False, blank=False,
        verbose_name="Room Member Status")

    def __str__(self):
        return f"{self.description}"

    class Meta:
        verbose_name_plural = 'RoomMemberStatuses'
        ordering = ['description']

class CheckStatus(models.Model):
    objects=MyManager()
    description = models.CharField(
        max_length=20, null=False, blank=False,
        verbose_name="Check Status")

    def __str__(self):
        return f"{self.description}"

    class Meta:
        verbose_name_plural = 'Check Statuses'
        ordering = ['description']

    @classmethod
    def get_default_pk(cls):
        status, created = cls.objects.get_or_create(
            description = cs.NOT_READY
        )
        return status.pk

class RoomStatus(models.Model):
    objects=MyManager()
    description = models.CharField(
        max_length=20, null=False, blank=False,
        verbose_name="Room Status")

    def __str__(self):
        return f"{self.description}"

    class Meta:
        verbose_name_plural = 'Room Statuses'
        ordering = ['description']

def get_default_check_status_pk():
    return CheckStatus.get_default_pk()

class Quiz(models.Model):
    objects=MyManager()
    # high-level quiz info
    # created by user
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True)
    # created_date
    created_date = models.DateTimeField(default=timezone.now, blank=True)
    # descriptive name for quiz
    title = models.CharField(
        max_length=100, null=False, blank=True,
        verbose_name="Title")
    status = models.ForeignKey(
        CheckStatus, on_delete=models.CASCADE, verbose_name="Quiz Status",
        default=get_default_check_status_pk,
        blank=True)
    # date quiz to be held
    quiz_date = models.DateField(default=date.today,
                                 verbose_name='Quiz Date')
#                                 validators=[validate_non_past_date])

    def __str__(self):
        return f"{self.created_date.date()}: {self.title}"

    class Meta:
        verbose_name_plural = 'Quizzes'
        ordering = ['created_date', 'title']

class Question(models.Model):
    objects=MyManager()
    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, related_name="questions_in_quiz", verbose_name="Quiz")
    question_number = models.PositiveIntegerField(
        null=False, blank=False, verbose_name='Question Number')
    question = models.CharField(
        max_length=255, null=False, blank=True, verbose_name="Question")
    transition_type = models.ForeignKey(
        TransitionType, on_delete=models.CASCADE, null=True, blank=True,
        verbose_name="Transition Type")
    media_url = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Media Url")
    default_image_number = models.PositiveIntegerField(
        null=True, blank=False, verbose_name='Default Image')
    time_limit = models.PositiveIntegerField(
        null=False, blank=False, verbose_name='Time Limit (secs)', default=30,
        validators=[MinValueValidator(1), MaxValueValidator(500)])
    score_multiplier = models.DecimalField(
        max_digits=4, decimal_places=2, null=False, blank=False, verbose_name='Score Multiplier',
        default=1, validators=[MinValueValidator(0), MaxValueValidator(4)])
    status = models.ForeignKey(
        CheckStatus, on_delete=models.CASCADE, verbose_name="Question Status",
        default=get_default_check_status_pk,)
    answer_1 = models.CharField(
        max_length=255, null=True, blank=True,
        verbose_name="Answer 1")
    correct_answer_1 = models.BooleanField(
        null=False, blank=False,
        verbose_name="Correct Answer")
    answer_2 = models.CharField(
        max_length=255, null=True, blank=True,
        verbose_name="Answer 2")
    correct_answer_2 = models.BooleanField(
        null=False, blank=False,
        verbose_name="Correct Answer")
    answer_3 = models.CharField(
        max_length=255, null=True, blank=True,
        verbose_name="Answer 3")
    correct_answer_3 = models.BooleanField(
        null=False, blank=False,
        verbose_name="Correct Answer")
    answer_4 = models.CharField(
        max_length=255, null=True, blank=True,
        verbose_name="Answer 4")
    correct_answer_4 = models.BooleanField(
        null=False, blank=False,
        verbose_name="Correct Answer")

    def __str__(self):
        return f"{self.question_number}: {self.question}"

    class Meta:
        ordering = ['question_number']
        #unique_together = [['quiz', 'question_number']]

    def get_fields(self):
        return {field.attname: getattr(self, field.attname) for field in self._meta.fields}

class Answer(models.Model):
    objects=MyManager()
    question = models.ForeignKey(Question, on_delete=models.PROTECT,
                                 related_name="answers_in_question",
                                 verbose_name="Question")
    answer_number = models.PositiveIntegerField(
        null=False, blank=False,
        verbose_name='Answer Number')
    answer = models.CharField(
        max_length=255, null=False, blank=False,
        verbose_name="Answer")
    correct_answer = models.BooleanField(
        null=False, blank=False,
        verbose_name="Correct Answer")

    def __str__(self):
        return f"{self.answer_number}: {self.answer}"

    class Meta:
        ordering = ['answer_number']

class QuizRoom(models.Model):
    objects=MyManager()
    room_number = models.PositiveIntegerField(
        null=False, blank=False, verbose_name='Room Number')
    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, verbose_name="Quiz")
    host = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="User")
    status = models.ForeignKey(
        RoomStatus, on_delete=models.CASCADE, verbose_name="Room Status")
    previous_question = models.ForeignKey(
        Question, on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='previous_questions_in_quizzes',
        verbose_name="Previous Question")
    current_question = models.ForeignKey(
        Question, on_delete=models.CASCADE,
        verbose_name="Current Question")
    question_start_time = models.DateTimeField(
        null=True, blank=True, verbose_name="Question Start Time")
    last_question = models.ForeignKey(
        Question, on_delete=models.CASCADE,
        related_name='last_questions_in_quizzes',
        verbose_name="Last Question")
    countdown_seconds_remaining = models.PositiveIntegerField(
        null=False, blank=False, verbose_name='Countdown Remaining')
    opened_date = models.DateField(default=date.today,
                                 verbose_name='Opened Date')
    preview = models.BooleanField(default=False)

class QuizRoomMember(models.Model):
    objects=MyManager()
    room = models.ForeignKey(QuizRoom, on_delete=models.CASCADE,
                             related_name="rooms_in_quiz",
                             verbose_name="Room Number")
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="users_in_room",
                             verbose_name="User")
    status = models.ForeignKey(RoomMemberStatus, on_delete=models.CASCADE,
                             related_name="users_in_room_status",
                             verbose_name="Room Member Status")
    nickname = models.CharField(
                             max_length=30, null=False, blank=False,
                             verbose_name="Nickname")
    joined_date = models.DateTimeField(default=timezone.now, blank=True)
    preview = models.BooleanField(default=False)
    joker_status = models.BooleanField(default=False, verbose_name="Joker Status")

    def __str__(self):
        return f"{self.room} {self.user} {self.nickname} {self.status}"

    class Meta:
        ordering = ['room', 'user']
        indexes = [
            models.Index(fields=['room']),
            models.Index(fields=['user']),
            models.Index(fields=['room', 'user']),
            models.Index(fields=['room', 'user', 'status']),
            models.Index(fields=['room', 'user', 'nickname'])
        ]

class QuizRoomMemberAnswer(models.Model):
    objects=MyManager()
    room_member = models.ForeignKey(QuizRoomMember, on_delete=models.CASCADE,
                                    related_name="answer_in_room_member",
                                    verbose_name="Room Member")
    room = models.ForeignKey(QuizRoom, on_delete=models.CASCADE,
                                    related_name="answer_in_room",
                                    verbose_name="Room")
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                                    related_name="answer_from_member",
                                    verbose_name="User")
    question = models.ForeignKey(
                                    Question, on_delete=models.CASCADE, null=True, blank=True,
                                    related_name="questions_in_room_member", verbose_name="Question")
    question_number = models.PositiveIntegerField(
                                    null=False, blank=False, verbose_name='Question Number')
    answer_number = models.PositiveIntegerField(
                                    null=True, blank=True, verbose_name='Answer Number')
    answer = models.ForeignKey(
                                    Answer, on_delete=models.CASCADE, null=True, blank=True,
                                    related_name="answers_in_room_member", verbose_name="Answer")
    response_time = models.DecimalField(
                                    max_digits=12, decimal_places=6,
                                    null=True, blank=True, verbose_name="Response Time")
    answer_score = models.PositiveIntegerField(
                                    null=True, blank=True, verbose_name='Running Score')
    running_score = models.PositiveIntegerField(
                                    null=True, blank=True, verbose_name='Prior Running Score')
    running_score_prior = models.PositiveIntegerField(
                                    null=True, blank=True, verbose_name='Answer Score')
    joker_status = models.BooleanField(default=False, verbose_name="Joker Status")

    def __str__(self):
        return f"{self.room} {self.user} {self.question} {self.answer}"

    class Meta:
        ordering = ['room', 'user', 'question', 'answer']
        unique_together = (('room', 'user', 'question', 'answer'))
        indexes = [
            models.Index(fields=['room']),
            models.Index(fields=['user']),
            models.Index(fields=['room', 'user']),
            models.Index(fields=['room', 'question'])
        ]

    @classmethod
    def get_previous_answer(cls, room_member:QuizRoomMember, current_question:Question):
        """
        Get previous answer from member, given member and current question

        :param room_member: room_member object as key
        :param current_question: current question object as key
        :return:
        """
        return (cls.objects.filter(
                room_member=room_member, question_number__lt=current_question.question_number)). \
                    order_by('-question_number').first()


