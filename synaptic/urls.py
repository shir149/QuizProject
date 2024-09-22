from django.urls import path

from . import views
from django.urls import reverse_lazy
from django.conf import settings
from django.conf.urls.static import static

# urlpatterns = [
#     path("", views.index2, name="index"),
#     path("<str:room_name>/", views.room, name="room"),
# ]

app_name="synaptic"
urlpatterns = [
    path("", views.index, name="index"),
    path("list_quizzes/", views.list_quizzes_view, name="list_quizzes"),
    path("list_questions/", views.list_questions_view, name="list_questions"),
    path("question/", views.question_view, name="question"),
    path("live_room/<int:room_number>", views.live_room_view, name="live_room"),
    path("live_room/", views.join_room_view, name="live_room_join"),
    path("join_room/", views.join_room_view, name="join_room"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("upload/", views.upload_quiz_spreadsheet_view, name="upload_quiz_spreadsheet"),
    path("password-reset/",
        views.PasswordResetView.as_view(
            template_name=f'{app_name}/password_reset.html',
            success_url=reverse_lazy(f'{app_name}:password_reset_done'),
            email_template_name=f'{app_name}/password_reset_email.html',
            subject_template_name=f'{app_name}/password_reset_email.txt'
        ),
        name='password_reset'),
    path("password-reset/done/",
        views.PasswordResetDoneView.as_view(template_name=f'{app_name}/password_reset_done.html'),
        name='password_reset_done'),
    path("password-reset-complete/",
        views.PasswordResetCompleteView.as_view(template_name=f'{app_name}/password_reset_complete.html'),
        name='password_reset_complete'),
    path("password-reset-confirm/<uidb64>/<token>/",
        views.PasswordResetConfirmView.as_view(template_name=f'{app_name}/password_reset_confirm.html',
                                                    success_url=reverse_lazy(f'{app_name}:password_reset_complete')),
        name='password_reset_confirm'),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)