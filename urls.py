"""Root URLconf for stapel-mailtrap — v1 canon mount (api-versioning.md §2, §6).

Canon: ``/<mod>/api/v1/...`` — the version segment sits right after ``api/``.
Hosts keep mounting ``include('stapel_mailtrap.urls')`` under ``mailtrap/``;
this module contributes the ``api/v1/`` prefix. The actual URL set (paths
inside unchanged, namespace ``mailtrap`` preserved) lives in ``urls_v1.py``.
"""
from django.urls import include, path

urlpatterns = [
    path('api/v1/', include('stapel_mailtrap.urls_v1')),
]
