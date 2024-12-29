from django.shortcuts import get_object_or_404, render
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm

from .models import Doctor, Schedule
from .utils import filter_published_objects


PAGES = 5


class RegisterView(CreateView):
    template_name = 'registration/registration_form.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('doctors:index')


class IndexView(ListView):
    template_name = 'doctors/index.html'
    model = Doctor
    paginate_by = PAGES

    def get_queryset(self):
        queryset = super().get_queryset()
        return filter_published_objects(queryset)


class DoctorDetailView(DetailView):
    model = Doctor
    template_name = 'doctors/detail.html'
    slug_url_kwarg = 'slug'
    context_object_name = 'doctor'

    def get_object(self, queryset=None):
        return self.model.objects.prefetch_related('schedules').get(slug=self.kwargs[self.slug_url_kwarg])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['schedule'] = self.object.schedules.all().order_by('day_of_week', 'start_time')
        return context
