"""i18n error keys of stapel-mailtrap.

Only ``error.<status>.<slug>`` keys leave this package — human-readable
strings are translations, never literals in responses
(docs/library-standard.md §3.6).
"""
from stapel_core.django.api.errors import register_service_errors

ERR_404_EMAIL_NOT_FOUND = "error.404.mailtrap_email_not_found"

STAPEL_MAILTRAP_ERRORS = {
    ERR_404_EMAIL_NOT_FOUND: "Trapped email not found",
}

register_service_errors(STAPEL_MAILTRAP_ERRORS)

__all__ = [
    "ERR_404_EMAIL_NOT_FOUND",
    "STAPEL_MAILTRAP_ERRORS",
]
