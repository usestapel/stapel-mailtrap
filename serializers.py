"""Serializers for the stapel-mailtrap API (dataclass-DTO backed).

Every view exposes a response serializer seam (SerializerSeamMixin); these are
the defaults. Swap one by subclassing the view and setting
``response_serializer_class`` — no need to rewrite the method body.
"""
from stapel_core.django.api.serializers import StapelDataclassSerializer

from .dto import TrappedEmailDetail, TrappedEmailListItem


class TrappedEmailListItemSerializer(StapelDataclassSerializer):
    class Meta:
        dataclass = TrappedEmailListItem


class TrappedEmailDetailSerializer(StapelDataclassSerializer):
    class Meta:
        dataclass = TrappedEmailDetail
