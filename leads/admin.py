from django.contrib import admin

from .models import (
    LeadSource,
    LeadTag,
    Lead,
    CallLog,
    FollowUp,
    LeadTimeline,
    LeadAuditLog
)


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = (
        'first_name',
        'phone',
        'status',
        'score',
        'country_interest',
        'assigned_to',
        'company'
    )

    search_fields = (
        'first_name',
        'last_name',
        'phone',
        'email'
    )

    list_filter = (
        'status',
        'country_interest',
        'company'
    )


admin.site.register(LeadSource)
admin.site.register(LeadTag)
admin.site.register(CallLog)
admin.site.register(FollowUp)
admin.site.register(LeadTimeline)
admin.site.register(LeadAuditLog)