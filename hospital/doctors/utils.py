from django.db.models import QuerySet
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.shortcuts import get_object_or_404

from .models import Appointment


def filter_published_objects(queryset):
    """Фильтрует объекты, оставляя только опубликованные."""
    if isinstance(queryset, QuerySet):
        return queryset.filter(is_published=True)
    return queryset


def user_is_owner_or_admin(model, field_name='patient'):
    """
    Декоратор для проверки, является ли текущий пользователь
    владельцем объекта или администратором.
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            object_id = kwargs.get('appointment_id') or kwargs.get('user_id')

            instance = get_object_or_404(model, pk=object_id)

            if model == Appointment and not instance.is_published:
                messages.error(request, "Запись на приём не найдена.")
                return HttpResponseForbidden("Запись на приём не найдена.")

            if field_name == 'id':
                owner_id = object_id
            else:
                owner = getattr(instance, field_name)
                owner_id = owner.id

            if request.user.id != owner_id and not request.user.is_staff:
                messages.error(request, "У вас нет прав для выполнения этого действия.")
                return HttpResponseForbidden("У вас нет прав для выполнения этого действия.")

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
