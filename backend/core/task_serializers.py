from rest_framework import serializers

from accounts.models import CustomUser

from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.SerializerMethodField()
    assigned_by_name = serializers.SerializerMethodField()
    lead_name = serializers.SerializerMethodField()
    student_name = serializers.SerializerMethodField()
    task_type_label = serializers.CharField(
        source='get_task_type_display',
        read_only=True,
    )
    status_label = serializers.CharField(
        source='get_status_display',
        read_only=True,
    )
    priority_label = serializers.CharField(
        source='get_priority_display',
        read_only=True,
    )

    class Meta:
        model = Task
        fields = [
            'id',
            'company',
            'task_type',
            'task_type_label',
            'title',
            'description',
            'notes',
            'lead',
            'lead_name',
            'student',
            'student_name',
            'assigned_to',
            'assigned_to_name',
            'assigned_by',
            'assigned_by_name',
            'status',
            'status_label',
            'priority',
            'priority_label',
            'due_date',
            'reminder_at',
            'completed_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'company',
            'assigned_by',
            'completed_at',
            'created_at',
            'updated_at',
        ]

    def get_assigned_to_name(self, obj):
        return _user_name(obj.assigned_to)

    def get_assigned_by_name(self, obj):
        return _user_name(obj.assigned_by)

    def get_lead_name(self, obj):
        if not obj.lead:
            return None

        return (
            f'{obj.lead.first_name} {obj.lead.last_name}'.strip()
        )

    def get_student_name(self, obj):
        if not obj.student:
            return None

        return obj.student.student_id


def _user_name(user):
    if not user:
        return None

    return user.get_full_name() or user.username
