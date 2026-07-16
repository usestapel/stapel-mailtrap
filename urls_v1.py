"""v1 URL set for stapel-mailtrap (api-versioning.md §2, §6).

No global prefix here — the root ``urls.py`` mounts this module under
``api/v1/`` and the host mounts that under ``mailtrap/``:

    path("mailtrap/", include("stapel_mailtrap.urls"))   # -> /mailtrap/api/v1/...

Routes (relative to the ``api/v1/`` mount): ``emails/`` (list),
``emails/<uuid:email_id>/`` (retrieve).
"""
from django.urls import path

from .views import TrappedEmailDetailView, TrappedEmailListView

app_name = "mailtrap"

urlpatterns = [
    path("emails/", TrappedEmailListView.as_view(), name="email-list"),
    path("emails/<uuid:email_id>/", TrappedEmailDetailView.as_view(), name="email-detail"),
]
