from django.urls import re_path

from . import consumers
from synaptic.consumers import QuizConsumer

websocket_urlpatterns = [
    re_path(r'synaptic/', QuizConsumer.as_asgi()),
    re_path(r'synaptic/live_room/[d+]', QuizConsumer.as_asgi()),
]