import json

from core.signals import Signal
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings
from django.core.mail import send_mail, BadHeaderError

_get_contribution_length_signal_params = ["grace_period"]
get_contribution_length_signal = Signal(providing_args=_get_contribution_length_signal_params)


def on_get_contribution_length_signal(sender, instance, **kwargs):
    grace_period = kwargs["grace_period"]
    # check if there is a grace period
    length_contribution = 0
    if grace_period:
        length_contribution = instance.benefit_plan.insurance_period + grace_period
    else:
        length_contribution = instance.benefit_plan.insurance_period
    return length_contribution


get_contribution_length_signal.connect(on_get_contribution_length_signal, dispatch_uid="on_contribution_length")