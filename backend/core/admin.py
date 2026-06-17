from django.contrib import admin

from .models import (
    Company,
    Branch,
    Task,
    TaskComment
)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name'
    )

    search_fields = (
        'name',
    )


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'company'
    )

    list_filter = (
        'company',
    )

    search_fields = (
        'name',
    )


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'assigned_to',
        'assigned_by',
        'status',
        'priority',
        'due_date',
        'created_at'
    )

    list_filter = (
        'status',
        'priority'
    )

    search_fields = (
        'title',
        'description'
    )


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):

    list_display = (
        'task',
        'user',
        'created_at'
    )

    search_fields = (
        'comment',
    )