"""Read-only admin for the trapped-email journal (docs/library-standard.md §2).

The trap is filled by the notifications provider / ``trap_email`` — never by
hand — so the admin is inspect-only; deletion is allowed for manual cleanup.
"""
from django.contrib import admin

from .models import TrappedEmail


@admin.register(TrappedEmail)
class TrappedEmailAdmin(admin.ModelAdmin):
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

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
