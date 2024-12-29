from django.urls import path

from . import views


app_name = 'doctors'


urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('doctors/<slug:slug>/', views.DoctorDetailView.as_view(), name='detail'),
]
