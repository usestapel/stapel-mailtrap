from django.apps import AppConfig


class MailtrapConfig(AppConfig):
    name = "stapel_mailtrap"
    label = "mailtrap"
    verbose_name = "Mail trap"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        # Import-time side effects: system checks + error-key registration.
        # Keep each in its own module. The email-provider adapter is resolved
        # lazily by stapel-notifications (dotted path), so nothing to register
        # here for it.
        from . import checks  # noqa: F401
        from . import errors  # noqa: F401
