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

admin.site.register(LeadSource)
admin.site.register(LeadTag)
admin.site.register(Lead)
admin.site.register(CallLog)
admin.site.register(FollowUp)
admin.site.register(LeadTimeline)
admin.site.register(LeadAuditLog)