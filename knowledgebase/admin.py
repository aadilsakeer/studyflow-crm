from django.contrib import admin

from .models import (
    Country,
    CountryGuide
)


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'code',
        'is_active'
    )

    search_fields = (
        'name',
    )


@admin.register(CountryGuide)
class CountryGuideAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'country',
        'is_active',
        'created_at'
    )

    list_filter = (
        'country',
        'is_active'
    )

    search_fields = (
        'title',
    )