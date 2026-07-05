"""URL patterns — no global prefix here, the host project mounts them:

    path("mailtrap/", include("stapel_mailtrap.urls"))

Routes (relative to the mount): ``emails/`` (list), ``emails/<uuid:email_id>/``
(retrieve).
"""
from django.urls import path

from .views import TrappedEmailDetailView, TrappedEmailListView

app_name = "mailtrap"

urlpatterns = [
    path("emails/", TrappedEmailListView.as_view(), name="email-list"),
    path("emails/<uuid:email_id>/", TrappedEmailDetailView.as_view(), name="email-detail"),
]
