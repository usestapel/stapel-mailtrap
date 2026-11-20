"""Canonical-prefix URLconf for contract emission.

The host mounts mailtrap at ``path("mailtrap/", include("stapel_mailtrap.urls"))``,
which yields ``/mailtrap/api/v1/...``; this URLconf reproduces that mount so
drf-spectacular emits the same paths and operationIds.
"""
from django.urls import include, path

urlpatterns = [
    path("mailtrap/", include("stapel_mailtrap.urls")),
]
