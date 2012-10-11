from django.dispatch import Signal

pin_finished = Signal(providing_args=["instance"])