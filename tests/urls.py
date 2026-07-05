from django.urls import include, path

urlpatterns = [
    path("mailtrap/", include("stapel_mailtrap.urls")),
]
