from django.core.management.base import BaseCommand
from synaptic.models import CheckStatus, RoomMemberStatus, RoomStatus, TransitionType

check_status_objects = [
    CheckStatus(description='Ready'),
    CheckStatus(description='Not Ready')
]
room_member_status_objects = [
    RoomMemberStatus(description="joined"),
    RoomMemberStatus(description="left")
]
room_status_objects = [
    RoomStatus(description="Waiting"),
    RoomStatus(description="Active"),
    RoomStatus(description="Question"),
    RoomStatus(description="Question Preview"),
    RoomStatus(description="Answer"),
    RoomStatus(description="Results"),
    RoomStatus(description="Score Multiplier"),
]
transition_type_objects = [
    TransitionType(description="Expand From Centre", function="expand_from_centre"),
    TransitionType(description="Horizontal Grow", function="horizontal_grow"),
    TransitionType(description="Scroll", function="scroll"),
]

class Command(BaseCommand):
    help = 'Seeds the database with initial reference data.'

    def handle(self, *args, **options):
        CheckStatus.objects.bulk_create(check_status_objects)
        RoomMemberStatus.objects.bulk_create(room_member_status_objects)
        RoomStatus.objects.bulk_create(room_status_objects)
        TransitionType.objects.bulk_create(transition_type_objects)
        self.stdout.write(self.style.SUCCESS('Successfully seeded the database.'))