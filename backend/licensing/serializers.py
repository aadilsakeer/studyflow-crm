from rest_framework import serializers

from .models import (
    BillingInvoice,
    BillingPayment,
    CompanySettings,
    CompanySubscription,
    SubscriptionPlan,
    TenantSupportAttachment,
    TenantSupportMessage,
    TenantSupportTicket,
)


class SubscriptionPlanSerializer(serializers.ModelSerializer):

    class Meta:
        model = SubscriptionPlan
        fields = (
            'id',
            'name',
            'code',
            'monthly_price',
            'yearly_price',
            'description',
            'trial_days',
            'max_users',
            'max_leads',
            'max_students',
            'max_whatsapp_per_month',
            'max_storage_mb',
        )


class CompanySubscriptionSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer(read_only=True)
    is_usable = serializers.SerializerMethodField()

    class Meta:
        model = CompanySubscription
        fields = (
            'plan',
            'status',
            'billing_cycle',
            'start_date',
            'end_date',
            'trial_ends_at',
            'current_period_start',
            'current_period_end',
            'auto_renew',
            'is_usable',
        )

    def get_is_usable(self, obj):
        return obj.is_usable()


class CompanySettingsSerializer(serializers.ModelSerializer):
    brand_logo_url = serializers.SerializerMethodField()
    brand_favicon_url = serializers.SerializerMethodField()

    class Meta:
        model = CompanySettings
        fields = (
            'timezone',
            'currency',
            'billing_email',
            'brand_name',
            'brand_primary_color',
            'brand_logo_url',
            'brand_favicon_url',
            'onboarding_step',
            'onboarding_completed_at',
            'storage_used_mb',
        )
        read_only_fields = (
            'onboarding_completed_at',
            'storage_used_mb',
            'brand_logo_url',
            'brand_favicon_url',
        )

    def _file_url(self, obj, field_name):
        file_field = getattr(obj, field_name, None)
        if not file_field:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(file_field.url)
        return file_field.url

    def get_brand_logo_url(self, obj):
        return self._file_url(obj, 'brand_logo')

    def get_brand_favicon_url(self, obj):
        return self._file_url(obj, 'brand_favicon')


class OnboardingRegisterSerializer(serializers.Serializer):
    company_name = serializers.CharField(max_length=255)
    admin_email = serializers.EmailField()
    admin_password = serializers.CharField(min_length=8, write_only=True)
    admin_first_name = serializers.CharField(required=False, allow_blank=True)
    admin_last_name = serializers.CharField(required=False, allow_blank=True)
    plan_code = serializers.CharField(required=False, allow_blank=True)


class CheckoutSerializer(serializers.Serializer):
    provider = serializers.ChoiceField(choices=['stripe', 'razorpay'])
    billing_cycle = serializers.ChoiceField(
        choices=['monthly', 'yearly'],
        default='monthly',
    )


class ChangePlanSerializer(serializers.Serializer):
    plan_code = serializers.CharField(max_length=50)


class CompanyModuleActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=[
        'enable', 'disable', 'trial', 'set_expiry', 'set_limits', 'remove',
    ])
    module_code = serializers.CharField(max_length=50)
    expires_at = serializers.DateTimeField(required=False, allow_null=True)
    trial_days = serializers.IntegerField(required=False, min_value=1, max_value=90)
    usage_limits = serializers.JSONField(required=False)


class BulkModuleAssignSerializer(serializers.Serializer):
    company_ids = serializers.ListField(
        child=serializers.IntegerField(), min_length=1,
    )
    module_codes = serializers.ListField(
        child=serializers.CharField(max_length=50), min_length=1,
    )
    action = serializers.ChoiceField(
        choices=['enable', 'disable', 'trial'], default='enable',
    )
    trial_days = serializers.IntegerField(required=False, min_value=1, max_value=90)


class BillingInvoiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = BillingInvoice
        fields = (
            'id',
            'invoice_number',
            'amount',
            'currency',
            'status',
            'period_start',
            'period_end',
            'due_date',
            'paid_at',
            'created_at',
        )


class BillingPaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = BillingPayment
        fields = (
            'id',
            'amount',
            'currency',
            'status',
            'provider',
            'paid_at',
            'created_at',
        )


class TenantSupportTicketSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = TenantSupportTicket
        fields = (
            'id',
            'subject',
            'description',
            'status',
            'priority',
            'sla_due_at',
            'sla_status',
            'created_by_name',
            'message_count',
            'resolved_at',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'sla_due_at',
            'sla_status',
            'resolved_at',
            'created_at',
            'updated_at',
        )

    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.username
        return None

    def get_message_count(self, obj):
        return obj.messages.count()


class TenantSupportTicketDetailSerializer(TenantSupportTicketSerializer):
    messages = serializers.SerializerMethodField()
    attachments = serializers.SerializerMethodField()

    class Meta(TenantSupportTicketSerializer.Meta):
        fields = TenantSupportTicketSerializer.Meta.fields + (
            'messages',
            'attachments',
        )

    def get_messages(self, obj):
        user = self.context.get('request').user
        qs = obj.messages.all()
        if not user.is_superuser:
            qs = qs.filter(is_internal=False)
        return TenantSupportMessageSerializer(qs, many=True).data

    def get_attachments(self, obj):
        return TenantSupportAttachmentSerializer(
            obj.attachments.all(),
            many=True,
            context=self.context,
        ).data


class TenantSupportMessageSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = TenantSupportMessage
        fields = (
            'id',
            'body',
            'is_internal',
            'author_name',
            'created_at',
        )
        read_only_fields = ('created_at',)

    def get_author_name(self, obj):
        if obj.author:
            return obj.author.get_full_name() or obj.author.username
        return 'System'


class TenantSupportAttachmentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = TenantSupportAttachment
        fields = ('id', 'filename', 'file_url', 'created_at')

    def get_file_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url


class TenantSupportTicketCreateSerializer(serializers.Serializer):
    subject = serializers.CharField(max_length=255)
    description = serializers.CharField()
    priority = serializers.ChoiceField(
        choices=[
            TenantSupportTicket.PRIORITY_LOW,
            TenantSupportTicket.PRIORITY_NORMAL,
            TenantSupportTicket.PRIORITY_HIGH,
            TenantSupportTicket.PRIORITY_URGENT,
        ],
        default=TenantSupportTicket.PRIORITY_NORMAL,
        required=False,
    )


class TenantSupportMessageCreateSerializer(serializers.Serializer):
    body = serializers.CharField()
    is_internal = serializers.BooleanField(default=False, required=False)


class TenantSupportTicketUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = TenantSupportTicket
        fields = ('status', 'priority', 'assigned_to')
