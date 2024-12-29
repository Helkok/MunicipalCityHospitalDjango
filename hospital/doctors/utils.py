from django.db.models import QuerySet


def filter_published_objects(queryset):
    if isinstance(queryset, QuerySet):
      return queryset.filter(is_published=True)
    return queryset