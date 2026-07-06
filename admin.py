"""Read-only admin for the trapped-email journal (docs/library-standard.md §2).

The trap is filled by the notifications provider / ``trap_email`` — never by
hand — so the admin is inspect-only. ``TrappedEmail`` is decorated
``@access.ops`` (admin-suite AS-5); subclassing ``StapelModelAdmin`` reads
that declaration and forbids add/change/delete for everyone, including the
superuser, in place of the hand-rolled ``has_*_permission`` overrides this
admin used before the rollout (delete used to be allowed here for manual
cleanup — it no longer is at the admin layer; retention still runs through
``services.purge_expired()``, which is unaffected by admin permissions).
"""
from django.contrib import admin

from stapel_core.django.admin.base import StapelModelAdmin

from .models import TrappedEmail


@admin.register(TrappedEmail)
class TrappedEmailAdmin(StapelModelAdmin):
    list_display = ["id", "subject", "to_email", "from_email", "scope_key", "created_at"]
    list_filter = ["scope_key", "created_at"]
    search_fields = ["to_email", "from_email", "subject", "scope_key"]
    readonly_fields = [
        "id",
        "to_email",
        "from_email",
        "subject",
        "body_html",
        "body_text",
        "attachments",
        "headers",
        "scope_key",
        "created_at",
    ]
    ordering = ["-created_at"]
