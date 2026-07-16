"""DRF views for stapel-mailtrap — the "Mail" ("Письма") API.

Read-only: the trap is filled by the notifications provider / the
``trap_email`` service, never through this API. Two endpoints — a paginated
list (filterable by ``scope_key``) and a single-message detail.

Default permission is staff/service only: trapped mail can contain OTPs and
magic links, so the OSS default is conservative. A host tightens or relaxes it
by subclassing and overriding ``permission_classes`` (and narrows visibility
per tenant via the ``SCOPE_PROVIDER`` seam).
"""
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.views import APIView
from stapel_core.django.api.errors import (
    StapelErrorResponse,
    StapelErrorSerializer,
    StapelResponse,
)
from stapel_core.django.api.pagination import CreatedAtAnchorPagination
from stapel_core.django.api.permissions import IsServiceRequest, IsStaffUser

from .dto import TrappedEmailDetail, TrappedEmailListItem
from .errors import ERR_404_EMAIL_NOT_FOUND
from .models import TrappedEmail
from .scope import get_scope_provider
from .serializers import TrappedEmailDetailSerializer, TrappedEmailListItemSerializer


class SerializerSeamMixin:
    """Overridable response-serializer seam for every mailtrap APIView."""

    response_serializer_class = None

    def get_response_serializer_class(self):
        return self.response_serializer_class


class MailPagination(CreatedAtAnchorPagination):
    page_size = 25
    max_page_size = 100


@extend_schema(tags=["Mail"])
class TrappedEmailListView(SerializerSeamMixin, APIView):
    """List trapped emails (newest first), paginated, filterable by scope."""

    permission_classes = [IsStaffUser | IsServiceRequest]
    pagination_class = MailPagination
    response_serializer_class = TrappedEmailListItemSerializer

    @extend_schema(
        operation_id="list_trapped_emails",
        summary="List trapped emails",
        parameters=[
            OpenApiParameter(
                name="scope_key",
                description="Restrict to a single opaque host scope.",
                required=False,
                type=str,
            )
        ],
        responses={200: TrappedEmailListItemSerializer(many=True)},
    )
    def get(self, request):  # noqa: R007
        queryset = TrappedEmail.objects.all()
        queryset = get_scope_provider().filter(queryset, request)

        scope_key = request.query_params.get("scope_key")
        if scope_key is not None:
            queryset = queryset.filter(scope_key=scope_key)

        paginator = MailPagination()
        page = paginator.paginate_queryset(queryset, request)

        response_cls = self.get_response_serializer_class()
        items = [
            response_cls(
                TrappedEmailListItem(  # noqa: SWAP002
                    id=str(row.id),
                    to_email=row.to_email,
                    from_email=row.from_email,
                    subject=row.subject,
                    scope_key=row.scope_key,
                    attachment_count=len(row.attachments or []),
                    created_at=row.created_at.isoformat(),
                )
            ).data
            for row in page
        ]
        return paginator.get_paginated_response(items)


@extend_schema(tags=["Mail"])
class TrappedEmailDetailView(SerializerSeamMixin, APIView):
    """Retrieve one trapped email (full bodies + attachment metadata)."""

    permission_classes = [IsStaffUser | IsServiceRequest]
    response_serializer_class = TrappedEmailDetailSerializer

    @extend_schema(
        operation_id="get_trapped_email",
        summary="Get a trapped email",
        responses={200: TrappedEmailDetailSerializer, 404: StapelErrorSerializer},
    )
    def get(self, request, email_id):  # noqa: R007
        queryset = get_scope_provider().filter(TrappedEmail.objects.all(), request)
        row = queryset.filter(id=email_id).first()
        if row is None:
            return StapelErrorResponse(status.HTTP_404_NOT_FOUND, ERR_404_EMAIL_NOT_FOUND)

        dto = TrappedEmailDetail(  # noqa: SWAP002
            id=str(row.id),
            to_email=row.to_email,
            from_email=row.from_email,
            subject=row.subject,
            body_html=row.body_html,
            body_text=row.body_text,
            attachments=row.attachments or [],
            headers=row.headers or {},
            scope_key=row.scope_key,
            created_at=row.created_at.isoformat(),
        )
        response_cls = self.get_response_serializer_class()
        return StapelResponse(response_cls(dto))
