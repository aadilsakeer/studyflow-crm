from rest_framework import serializers


class EmployeeCreateSerializer(serializers.Serializer):
    company_id = serializers.IntegerField()
    employee_code = serializers.CharField(max_length=32)
    full_name = serializers.CharField(max_length=255)
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    designation = serializers.CharField(required=False, allow_blank=True)
    department_id = serializers.IntegerField(required=False, allow_null=True)
    shift_id = serializers.IntegerField(required=False, allow_null=True)
    user_id = serializers.IntegerField(required=False, allow_null=True)
    salary_structure = serializers.DictField(required=False)
    leave_balance = serializers.DictField(required=False)
    joined_at = serializers.DateField(required=False, allow_null=True)


class CheckInOutSerializer(serializers.Serializer):
    employee_id = serializers.IntegerField()
    latitude = serializers.DecimalField(max_digits=10, decimal_places=7, required=False, allow_null=True)
    longitude = serializers.DecimalField(max_digits=10, decimal_places=7, required=False, allow_null=True)


class LeaveApplySerializer(serializers.Serializer):
    employee_id = serializers.IntegerField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    leave_type = serializers.CharField(required=False, default='annual')
    reason = serializers.CharField(required=False, allow_blank=True)


class LeaveReviewSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['approved', 'rejected'])
    reviewer_notes = serializers.CharField(required=False, allow_blank=True)


class PayrollCreateSerializer(serializers.Serializer):
    employee_id = serializers.IntegerField()
    month = serializers.CharField(max_length=20)
    year = serializers.IntegerField()
    basic_salary = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    deductions = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, default=0)
    salary_structure = serializers.DictField(required=False)


class PayrollStatusSerializer(serializers.Serializer):
    payment_status = serializers.ChoiceField(choices=['pending', 'processed', 'paid'])


class AssetAssignSerializer(serializers.Serializer):
    employee_id = serializers.IntegerField()
    asset_type = serializers.ChoiceField(choices=['laptop', 'phone', 'accessory'])
    asset_name = serializers.CharField(max_length=255)
    serial_number = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)
