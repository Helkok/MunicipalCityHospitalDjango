from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView
from django.views.generic.edit import FormView

from .forms import AppointmentForm, UserEditForm
from .models import Doctor, Appointment, Schedule
from .utils import filter_published_objects, user_is_owner_or_admin


PAGES = 5


class RegisterView(CreateView):
    template_name = "registration/registration_form.html"
    form_class = UserCreationForm
    success_url = reverse_lazy("doctors:index")


class IndexView(ListView):
    template_name = "doctors/index.html"
    model = Doctor
    paginate_by = PAGES

    def get_queryset(self):
        queryset = super().get_queryset()
        return filter_published_objects(queryset)


class DoctorDetailView(DetailView):
    model = Doctor
    template_name = "doctors/detail.html"
    slug_url_kwarg = "slug"
    context_object_name = "doctor"

    def get_object(self, queryset=None):
        return get_object_or_404(
            Doctor.objects.filter(is_published=True).prefetch_related("schedules"),
            slug=self.kwargs[self.slug_url_kwarg],
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["schedule"] = self.object.schedules.filter(
            doctor__is_published=True
        ).order_by("day_of_week", "start_time")
        return context


@login_required
def create_appointment(request, slug):
    doctor = get_object_or_404(
        filter_published_objects(Doctor.objects),
        slug=slug
    )

    if request.method == "POST":
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            date = request.POST.get("date")
            if date:
                try:
                    selected_date = timezone.datetime.strptime(date, "%Y-%m-%d").date()
                except ValueError:
                    return JsonResponse({"errors": "Неверный формат даты"}, status=400)

                available_times = []

                day_of_week = selected_date.isoweekday()
                schedule_entries = Schedule.objects.select_related('doctor').filter(
                    doctor=doctor, day_of_week=day_of_week
                )

                occupied_times = set(
                    Appointment.objects.select_related('doctor').filter(
                        doctor=doctor,
                        date=selected_date,
                        status__in=["scheduled", "completed"],
                    ).values_list("time", flat=True)
                )

                for entry in schedule_entries:
                    current_time = entry.start_time
                    while current_time < entry.end_time:
                        if current_time not in occupied_times:
                            available_times.append(current_time.strftime("%H:%M"))
                        current_time = (
                            timezone.datetime.combine(selected_date, current_time)
                            + timezone.timedelta(minutes=30)
                        ).time()

                return JsonResponse({"times": available_times})
            else:
                return JsonResponse({"errors": "Не указана дата"}, status=400)

        form = AppointmentForm(request.POST, doctor=doctor)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.doctor = doctor
            appointment.patient = request.user
            appointment.save()
            messages.success(request, "Вы успешно записались на приём!")
            return redirect("doctors:detail", slug=doctor.slug)
        else:
            messages.error(
                request, "Не удалось записаться на приём. Пожалуйста, проверьте данные."
            )
    else:
        form = AppointmentForm(doctor=doctor, initial={"date": timezone.now().date()})

    context = {
        "doctor": doctor,
        "form": form,
    }
    return render(request, "doctors/create_appointment.html", context)


@login_required
@user_is_owner_or_admin(Appointment)
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(
        filter_published_objects(Appointment.objects.select_related('patient')),
        id=appointment_id
    )

    if request.method == "POST":
        appointment.status = "cancelled"
        appointment.save()
        messages.success(request, "Ваша запись на приём успешно отменена.")
        return redirect("doctors:index")

    context = {"appointment": appointment}
    return render(request, "doctors/cancel_appointment.html", context)


@login_required
@user_is_owner_or_admin(User, field_name='id')
def profile(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    appointments = filter_published_objects(
        Appointment.objects.filter(patient=user, status="scheduled")
        .prefetch_related("doctor", "patient")
    ).order_by("date", "time")

    paginator = Paginator(appointments, PAGES)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "profile": user,
        "page_obj": page_obj,
        "appointments": page_obj.object_list,
    }
    return render(request, "doctors/profile.html", context)


class EditProfileView(LoginRequiredMixin, FormView):
    template_name = "doctors/edit_profile.html"
    form_class = UserEditForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Профиль успешно обновлен!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("doctors:profile", kwargs={"user_id": self.request.user.id})
