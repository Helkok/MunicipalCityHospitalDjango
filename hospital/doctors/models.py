from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.dispatch import receiver


class IsPublished(models.Model):
    is_published = models.BooleanField(default=True, verbose_name='Обубликован')

    class Meta:
        abstract = True


class Doctor(IsPublished):
    name = models.CharField(max_length=255, verbose_name="ФИО врача")
    specialization = models.CharField(max_length=255, verbose_name="Специализация")
    office = models.CharField(max_length=50, verbose_name="Номер кабинета")
    slug = models.SlugField(max_length=50, unique=True, verbose_name="Слаг")
    is_published = models.BooleanField(default=True, verbose_name='Обубликован')
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


class Appointment(IsPublished):
    STATUS_CHOICES = (
        ('scheduled', 'Запланирован'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен'),
    )
    doctor = models.ForeignKey(
        Doctor, 
        on_delete=models.CASCADE, 
        verbose_name="Врач", 
        related_name='appoinments'
    )
    patient = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name="Пациент", 
        related_name='appoinments'
    )
    date = models.DateField(verbose_name="Дата приёма")
    time = models.TimeField(verbose_name="Время приёма")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled', verbose_name="Статус")

    def __str__(self):
        return f"Приём у {self.doctor.name} на {self.date} в {self.time}"

    def clean(self):
        conflicting_appointments = Appointment.objects.filter(
            date=self.date,
            time=self.time,
            doctor__office=self.doctor.office
        ).exclude(pk=self.pk)

        if conflicting_appointments.exists():
            raise ValidationError("Этот кабинет уже занят на указанное время.")

    class Meta:
        verbose_name = "Запись на приём"
        verbose_name_plural = "Записи на приём"


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
    
    def save(self, *args, **kwargs):
        if not self.office:
            self.office = self.doctor.office
        super().save(*args, **kwargs)