from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.dispatch import receiver
from unidecode import unidecode


class IsPublished(models.Model):
    is_published = models.BooleanField(default=True, verbose_name='Опубликован')

    class Meta:
        abstract = True


class Doctor(IsPublished):
    name = models.CharField(max_length=255, verbose_name="ФИО врача")
    specialization = models.CharField(max_length=255, verbose_name="Специализация")
    office = models.CharField(max_length=50, verbose_name="Номер кабинета")
    slug = models.SlugField(max_length=50, unique=True, verbose_name="Слаг")
    image = models.ImageField(
        verbose_name='Изображение',
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.name} ({self.specialization})"

    class Meta:
        verbose_name = "Врач"
        verbose_name_plural = "Врачи"
        ordering = ("slug",)


@receiver(pre_save, sender=Doctor)
def create_doctor_slug(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(unidecode(instance.name))


class Appointment(IsPublished):
    STATUS_CHOICES = (
        ('scheduled', 'Запланирован'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен'),
    )
    APPOINTMENT_STATUSES = ['scheduled', 'completed']

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        verbose_name="Врач",
        related_name='appointments'
    )
    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пациент",
        related_name='appointments'
    )
    date = models.DateField(verbose_name="Дата приёма")
    time = models.TimeField(verbose_name="Время приёма")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled', verbose_name="Статус")

    def __str__(self):
        return f"Приём у {self.doctor.name} на {self.date} в {self.time}"

    def is_time_available(self):
        """Проверяет, доступно ли время для записи."""
        conflicting_appointments = Appointment.objects.filter(
            doctor=self.doctor,
            date=self.date,
            time=self.time,
            status__in=self.APPOINTMENT_STATUSES,
            is_published=True
        ).exclude(pk=self.pk)

        return not conflicting_appointments.exists()

    class Meta:
        verbose_name = "Запись на приём"
        verbose_name_plural = "Записи на приём"
        indexes = [
            models.Index(fields=['doctor', 'date', 'time']),
            models.Index(fields=['date', 'time']),
            models.Index(fields=['status']),
        ]


class Schedule(models.Model):
    DAYS_OF_WEEK = (
        (1, 'Понедельник'),
        (2, 'Вторник'),
        (3, 'Среда'),
        (4, 'Четверг'),
        (5, 'Пятница'),
        (6, 'Суббота'),
        (7, 'Воскресенье'),
    )

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, verbose_name="Врач", related_name='schedules')
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK, verbose_name="День недели")
    start_time = models.TimeField(verbose_name="Время начала приёма")
    end_time = models.TimeField(verbose_name="Время окончания приёма")
    office = models.CharField(max_length=50, verbose_name="Номер кабинета", blank=True)

    def __str__(self):
        return f"Расписание {self.doctor.name} на {self.get_day_of_week_display()}"

    class Meta:
        unique_together = [['doctor', 'day_of_week', 'start_time'], ['office', 'day_of_week', 'start_time']]
        verbose_name = "Расписание"
        verbose_name_plural = "Расписания"
        indexes = [
            models.Index(fields=['doctor', 'day_of_week']),
            models.Index(fields=['office', 'day_of_week']),
        ]

    def save(self, *args, **kwargs):
        self.office = getattr(self.doctor, 'office', self.office)
        super().save(*args, **kwargs)
