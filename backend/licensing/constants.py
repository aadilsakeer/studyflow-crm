SUBSCRIPTION_STATUS_TRIAL = 'trial'
SUBSCRIPTION_STATUS_ACTIVE = 'active'
SUBSCRIPTION_STATUS_PAST_DUE = 'past_due'
SUBSCRIPTION_STATUS_CANCELLED = 'cancelled'
SUBSCRIPTION_STATUS_EXPIRED = 'expired'

SUBSCRIPTION_STATUSES = (
    SUBSCRIPTION_STATUS_TRIAL,
    SUBSCRIPTION_STATUS_ACTIVE,
    SUBSCRIPTION_STATUS_PAST_DUE,
    SUBSCRIPTION_STATUS_CANCELLED,
    SUBSCRIPTION_STATUS_EXPIRED,
)

BILLING_CYCLE_MONTHLY = 'monthly'
BILLING_CYCLE_YEARLY = 'yearly'

BILLING_CYCLES = (
    BILLING_CYCLE_MONTHLY,
    BILLING_CYCLE_YEARLY,
)

LIMIT_USERS = 'users'
LIMIT_LEADS = 'leads'
LIMIT_STUDENTS = 'students'
LIMIT_WHATSAPP = 'whatsapp'
LIMIT_STORAGE = 'storage'

INVOICE_STATUS_DRAFT = 'draft'
INVOICE_STATUS_ISSUED = 'issued'
INVOICE_STATUS_PAID = 'paid'
INVOICE_STATUS_VOID = 'void'

PAYMENT_STATUS_PENDING = 'pending'
PAYMENT_STATUS_PAID = 'paid'
PAYMENT_STATUS_FAILED = 'failed'
PAYMENT_STATUS_REFUNDED = 'refunded'

PROVIDER_STRIPE = 'stripe'
PROVIDER_RAZORPAY = 'razorpay'
PROVIDER_MANUAL = 'manual'

PLAN_STARTER = 'starter'
PLAN_GROWTH = 'growth'
PLAN_ENTERPRISE = 'enterprise'
PLAN_CUSTOM = 'custom'

MODULE_CATALOG = (
    ('crm', 'CRM'),
    ('admissions', 'Admissions'),
    ('studentportal', 'Student Portal'),
    ('whatsapp', 'WhatsApp'),
    ('automation', 'Workflow Automation'),
    ('hrm', 'HRMS'),
    ('ai', 'AI'),
    ('knowledgebase', 'Knowledge Base'),
    ('document_intelligence', 'Document Intelligence'),
    ('billing', 'Billing & Invoicing'),
)

AUDIT_MODULE_LICENSING = 'licensing'
