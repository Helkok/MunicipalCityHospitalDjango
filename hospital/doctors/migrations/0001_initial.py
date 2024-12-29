# Generated by Django 3.2.16 on 2024-12-28 12:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Doctor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='ФИО врача')),
                ('specialization', models.CharField(max_length=255, verbose_name='Специализация')),
                ('office', models.CharField(max_length=50, verbose_name='Номер кабинета')),
                ('slug', models.SlugField(blank=True, unique=True, verbose_name='Слаг (заполняется автоматически)')),
            ],
            options={
                'verbose_name': 'Врач',
                'verbose_name_plural': 'Врачи',
            },
        ),
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='Дата приёма')),
                ('time', models.TimeField(verbose_name='Время приёма')),
                ('status', models.CharField(choices=[('scheduled', 'Запланирован'), ('completed', 'Завершен'), ('cancelled', 'Отменен')], default='scheduled', max_length=20, verbose_name='Статус')),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='doctors.doctor', verbose_name='Врач')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пациент')),
            ],
            options={
                'verbose_name': 'Запись на приём',
                'verbose_name_plural': 'Записи на приём',
            },
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_of_week', models.IntegerField(choices=[(1, 'Понедельник'), (2, 'Вторник'), (3, 'Среда'), (4, 'Четверг'), (5, 'Пятница'), (6, 'Суббота'), (7, 'Воскресенье')], verbose_name='День недели')),
                ('start_time', models.TimeField(verbose_name='Время начала приёма')),
                ('end_time', models.TimeField(verbose_name='Время окончания приёма')),
                ('office', models.CharField(blank=True, max_length=50, verbose_name='Номер кабинета')),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='doctors.doctor', verbose_name='Врач')),
            ],
            options={
                'verbose_name': 'Расписание',
                'verbose_name_plural': 'Расписания',
                'unique_together': {('office', 'day_of_week', 'start_time'), ('doctor', 'day_of_week', 'start_time')},
            },
        ),
    ]