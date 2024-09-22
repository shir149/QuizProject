from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

def validate_non_past_date(value):
    if value < timezone.localdate():
        raise ValidationError (_("Cannot be in the past"))
    return value