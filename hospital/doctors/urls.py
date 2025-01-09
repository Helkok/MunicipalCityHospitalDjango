from django.urls import path

from . import views


app_name = "doctors"


urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("doctors/<slug:slug>/", views.DoctorDetailView.as_view(), name="detail"),
    path(
        "doctors/<slug:slug>/appointment/",
        views.create_appointment,
        name="create_appointment",
    ),
    path(
        "appointments/<int:appointment_id>/cancel/",
        views.cancel_appointment,
        name="cancel_appointment",
    ),
    path("profile/<int:user_id>/", views.profile, name="profile"),
    path("edit-profile/", views.EditProfileView.as_view(), name="edit_profile"),
]
