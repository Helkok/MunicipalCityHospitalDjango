from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.utils import timezone

from .models import Appointment, Schedule


class AppointmentForm(forms.ModelForm):
    """Форма записи на прием к врачу."""

    date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}), initial=timezone.localdate()
    )

    class Meta:
        model = Appointment
        fields = ["date", "time"]
        widgets = {
            "time": forms.Select(),
        }

    def __init__(self, *args, doctor=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.doctor = doctor
        if self.doctor:
            selected_date = self.get_selected_date()
            self.fields["time"].choices = self._get_available_times(selected_date)

    def get_selected_date(self):
        if self.is_bound:
            selected_date_str = self.data.get("date")
            if selected_date_str:
                try:
                    return timezone.datetime.strptime(selected_date_str, "%Y-%m-%d").date()
                except ValueError:
                    pass
        return timezone.localdate()

    def _get_available_times(self, selected_date):
        """
        Возвращает список доступных временных интервалов для записи на прием к врачу.
        """
        day_of_week = selected_date.isoweekday()
        if not hasattr(self, "_schedule_cache"):
            self._schedule_cache = {}

        if day_of_week not in self._schedule_cache:
            self._schedule_cache[day_of_week] = Schedule.objects.filter(
                doctor=self.doctor, day_of_week=day_of_week
            )

        schedule_entries = self._schedule_cache[day_of_week]

        occupied_times = set(
            Appointment.objects.filter(
                doctor=self.doctor,
                date=selected_date,
                status__in=["scheduled", "completed"],
            ).values_list("time", flat=True)
        )

        available_times = []
        for entry in schedule_entries:
            current_time = entry.start_time
            while current_time < entry.end_time:
                if current_time not in occupied_times:
                    available_times.append(
                        (current_time.strftime("%H:%M"), current_time.strftime("%H:%M"))
                    )
                current_time = (
                    timezone.datetime.combine(selected_date, current_time)
                    + timezone.timedelta(minutes=30)
                ).time()

        return available_times

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get("date")
        time = cleaned_data.get("time")

        if date and time:
            if Appointment.objects.filter(
                doctor=self.doctor,
                date=date,
                time=time,
                status__in=["scheduled", "completed"],
            ).exists():
                raise forms.ValidationError(
                    f"Время {time.strftime('%H:%M')} на {date.strftime('%Y-%m-%d')} уже занято."
                )

        return cleaned_data


class UserEditForm(ModelForm):
    """Форма редактирования данных пользователя."""

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")
