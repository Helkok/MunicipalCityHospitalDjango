# Generated by Django 3.2.16 on 2024-12-28 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doctors', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='is_published',
            field=models.BooleanField(default=True, verbose_name='Обубликован'),
        ),
        migrations.AddField(
            model_name='doctor',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='', verbose_name='Изображение'),
        ),
        migrations.AddField(
            model_name='doctor',
            name='is_published',
            field=models.BooleanField(default=True, verbose_name='Обубликован'),
        ),
        migrations.AlterField(
            model_name='doctor',
            name='slug',
            field=models.SlugField(unique=True, verbose_name='Слаг'),
        ),
    ]