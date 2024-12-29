# Generated by Django 3.2.16 on 2024-12-28 15:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('doctors', '0003_alter_doctor_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='doctor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appoinments', to='doctors.doctor', verbose_name='Врач'),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='patient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appoinments', to=settings.AUTH_USER_MODEL, verbose_name='Пациент'),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='doctor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedules', to='doctors.doctor', verbose_name='Врач'),
        ),
    ]