# Generated by Django 3.2.16 on 2024-12-28 14:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('doctors', '0002_auto_20241228_1953'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='doctor',
            options={'ordering': ('slug',), 'verbose_name': 'Врач', 'verbose_name_plural': 'Врачи'},
        ),
    ]
