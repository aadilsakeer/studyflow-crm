# Role names (must match seed_rbac)
ROLE_ADMIN = "Admin"
ROLE_MANAGER = "Manager"
ROLE_COUNSELLOR = "Counsellor"
ROLE_TELECALLER = "Telecaller"
ROLE_FINANCE = "Finance"
ROLE_VIEWER = "Viewer"
ROLE_VISA_TEAM = "Visa Team"

# Permission codes
PERM_DASHBOARD_VIEW = "dashboard.view"

PERM_LEADS_VIEW = "leads.view"
PERM_LEADS_ADD = "leads.add"
PERM_LEADS_CHANGE = "leads.change"
PERM_LEADS_DELETE = "leads.delete"
PERM_LEADS_CONVERT = "leads.convert"
PERM_LEADS_RESTORE = "leads.restore"
PERM_LEADS_ASSIGN = "leads.assign"
PERM_LEADS_IMPORT = "leads.import"
PERM_LEADS_QUALIFY = "leads.qualify"
PERM_LEADS_ASSIGN_COUNSELLOR = "leads.assign_counsellor"

PERM_FOLLOWUPS_VIEW = "followups.view"
PERM_FOLLOWUPS_ADD = "followups.add"
PERM_FOLLOWUPS_CHANGE = "followups.change"
PERM_FOLLOWUPS_DELETE = "followups.delete"

PERM_TASKS_VIEW = "tasks.view"
PERM_TASKS_ADD = "tasks.add"
PERM_TASKS_CHANGE = "tasks.change"
PERM_TASKS_DELETE = "tasks.delete"

PERM_COMMUNICATIONS_VIEW = "communications.view"
PERM_COMMUNICATIONS_ADD = "communications.add"
PERM_COMMUNICATIONS_CHANGE = "communications.change"
PERM_COMMUNICATIONS_DELETE = "communications.delete"

PERM_CALLLOGS_VIEW = "calllogs.view"
PERM_CALLLOGS_ADD = "calllogs.add"
PERM_CALLLOGS_CHANGE = "calllogs.change"
PERM_CALLLOGS_DELETE = "calllogs.delete"

PERM_STUDENTS_VIEW = "students.view"
PERM_STUDENTS_ADD = "students.add"
PERM_STUDENTS_CHANGE = "students.change"
PERM_STUDENTS_DELETE = "students.delete"
PERM_STUDENTS_RESTORE = "students.restore"

PERM_APPLICATIONS_VIEW = "applications.view"
PERM_APPLICATIONS_ADD = "applications.add"
PERM_APPLICATIONS_CHANGE = "applications.change"
PERM_APPLICATIONS_DELETE = "applications.delete"
PERM_APPLICATIONS_RESTORE = "applications.restore"

PERM_UNIVERSITIES_VIEW = "universities.view"
PERM_UNIVERSITIES_ADD = "universities.add"
PERM_UNIVERSITIES_CHANGE = "universities.change"
PERM_UNIVERSITIES_DELETE = "universities.delete"

PERM_DOCUMENTS_VIEW = "documents.view"
PERM_DOCUMENTS_ADD = "documents.add"
PERM_DOCUMENTS_CHANGE = "documents.change"
PERM_DOCUMENTS_DELETE = "documents.delete"
PERM_DOCUMENTS_RESTORE = "documents.restore"

PERM_OFFERLETTERS_VIEW = "offerletters.view"
PERM_OFFERLETTERS_ADD = "offerletters.add"
PERM_OFFERLETTERS_CHANGE = "offerletters.change"
PERM_OFFERLETTERS_DELETE = "offerletters.delete"
PERM_OFFERLETTERS_RESTORE = "offerletters.restore"

PERM_VISAS_VIEW = "visas.view"
PERM_VISAS_ADD = "visas.add"
PERM_VISAS_CHANGE = "visas.change"
PERM_VISAS_DELETE = "visas.delete"
PERM_VISAS_RESTORE = "visas.restore"
PERM_VISAS_SUBMIT = "visas.submit"
PERM_VISAS_PROCESS = "visas.process"
PERM_VISAS_APPROVE = "visas.approve"
PERM_VISAS_REJECT = "visas.reject"

PERM_PAYMENTS_VIEW = "payments.view"
PERM_PAYMENTS_ADD = "payments.add"
PERM_PAYMENTS_CHANGE = "payments.change"
PERM_PAYMENTS_DELETE = "payments.delete"
PERM_INVOICES_VIEW = "invoices.view"
PERM_INVOICES_ADD = "invoices.add"
PERM_INVOICES_CHANGE = "invoices.change"
PERM_INVOICES_DELETE = "invoices.delete"

PERM_AGENTS_VIEW = "agents.view"
PERM_AGENTS_ADD = "agents.add"
PERM_AGENTS_CHANGE = "agents.change"
PERM_AGENTS_DELETE = "agents.delete"

PERM_PARTNERS_VIEW = "partners.view"
PERM_PARTNERS_ADD = "partners.add"
PERM_PARTNERS_CHANGE = "partners.change"
PERM_PARTNERS_DELETE = "partners.delete"

PERM_SETTINGS_MANAGE = "settings.manage"

PERM_HRM_VIEW = "hrm.view"
PERM_HRM_ADD = "hrm.add"
PERM_HRM_CHANGE = "hrm.change"
PERM_HRM_DELETE = "hrm.delete"

PERM_RECRUITMENT_VIEW = "recruitment.view"
PERM_RECRUITMENT_ADD = "recruitment.add"
PERM_RECRUITMENT_CHANGE = "recruitment.change"
PERM_RECRUITMENT_DELETE = "recruitment.delete"

PERM_WORKVISA_VIEW = "workvisa.view"
PERM_WORKVISA_ADD = "workvisa.add"
PERM_WORKVISA_CHANGE = "workvisa.change"
PERM_WORKVISA_DELETE = "workvisa.delete"

PERM_WHATSAPP_VIEW = "whatsapp.view"
PERM_WHATSAPP_ADD = "whatsapp.add"
PERM_WHATSAPP_CHANGE = "whatsapp.change"
PERM_WHATSAPP_DELETE = "whatsapp.delete"

PERM_REPORTS_VIEW = "reports.view"
PERM_REPORTS_ADD = "reports.add"
PERM_REPORTS_CHANGE = "reports.change"
PERM_REPORTS_DELETE = "reports.delete"

PERM_NOTIFICATIONS_VIEW = "notifications.view"
PERM_NOTIFICATIONS_ADD = "notifications.add"
PERM_NOTIFICATIONS_CHANGE = "notifications.change"
PERM_NOTIFICATIONS_DELETE = "notifications.delete"

PERM_CLIENTPORTAL_VIEW = "clientportal.view"
PERM_CLIENTPORTAL_ADD = "clientportal.add"
PERM_CLIENTPORTAL_CHANGE = "clientportal.change"
PERM_CLIENTPORTAL_DELETE = "clientportal.delete"

ALL_PERMISSIONS = [
    (PERM_DASHBOARD_VIEW, "View Dashboard"),
    (PERM_LEADS_VIEW, "View Leads"),
    (PERM_LEADS_ADD, "Add Leads"),
    (PERM_LEADS_CHANGE, "Change Leads"),
    (PERM_LEADS_DELETE, "Delete Leads"),
    (PERM_LEADS_CONVERT, "Convert Leads"),
    (PERM_LEADS_RESTORE, "Restore Leads"),
    (PERM_LEADS_ASSIGN, "Assign Leads"),
    (PERM_LEADS_IMPORT, "Import Leads"),
    (PERM_LEADS_QUALIFY, "Qualify Leads"),
    (PERM_LEADS_ASSIGN_COUNSELLOR, "Assign Counsellor"),
    (PERM_FOLLOWUPS_VIEW, "View Follow Ups"),
    (PERM_FOLLOWUPS_ADD, "Add Follow Ups"),
    (PERM_FOLLOWUPS_CHANGE, "Change Follow Ups"),
    (PERM_FOLLOWUPS_DELETE, "Delete Follow Ups"),
    (PERM_TASKS_VIEW, "View Tasks"),
    (PERM_TASKS_ADD, "Add Tasks"),
    (PERM_TASKS_CHANGE, "Change Tasks"),
    (PERM_TASKS_DELETE, "Delete Tasks"),
    (PERM_COMMUNICATIONS_VIEW, "View Communications"),
    (PERM_COMMUNICATIONS_ADD, "Add Communications"),
    (PERM_COMMUNICATIONS_CHANGE, "Change Communications"),
    (PERM_COMMUNICATIONS_DELETE, "Delete Communications"),
    (PERM_CALLLOGS_VIEW, "View Call Logs"),
    (PERM_CALLLOGS_ADD, "Add Call Logs"),
    (PERM_CALLLOGS_CHANGE, "Change Call Logs"),
    (PERM_CALLLOGS_DELETE, "Delete Call Logs"),
    (PERM_STUDENTS_VIEW, "View Students"),
    (PERM_STUDENTS_ADD, "Add Students"),
    (PERM_STUDENTS_CHANGE, "Change Students"),
    (PERM_STUDENTS_DELETE, "Delete Students"),
    (PERM_STUDENTS_RESTORE, "Restore Students"),
    (PERM_APPLICATIONS_VIEW, "View Applications"),
    (PERM_APPLICATIONS_ADD, "Add Applications"),
    (PERM_APPLICATIONS_CHANGE, "Change Applications"),
    (PERM_APPLICATIONS_DELETE, "Delete Applications"),
    (PERM_APPLICATIONS_RESTORE, "Restore Applications"),
    (PERM_UNIVERSITIES_VIEW, "View Universities"),
    (PERM_UNIVERSITIES_ADD, "Add Universities"),
    (PERM_UNIVERSITIES_CHANGE, "Change Universities"),
    (PERM_UNIVERSITIES_DELETE, "Delete Universities"),
    (PERM_DOCUMENTS_VIEW, "View Documents"),
    (PERM_DOCUMENTS_ADD, "Add Documents"),
    (PERM_DOCUMENTS_CHANGE, "Change Documents"),
    (PERM_DOCUMENTS_DELETE, "Delete Documents"),
    (PERM_DOCUMENTS_RESTORE, "Restore Documents"),
    (PERM_OFFERLETTERS_VIEW, "View Offer Letters"),
    (PERM_OFFERLETTERS_ADD, "Add Offer Letters"),
    (PERM_OFFERLETTERS_CHANGE, "Change Offer Letters"),
    (PERM_OFFERLETTERS_DELETE, "Delete Offer Letters"),
    (PERM_OFFERLETTERS_RESTORE, "Restore Offer Letters"),
    (PERM_VISAS_VIEW, "View Visas"),
    (PERM_VISAS_ADD, "Add Visas"),
    (PERM_VISAS_CHANGE, "Change Visas"),
    (PERM_VISAS_DELETE, "Delete Visas"),
    (PERM_VISAS_RESTORE, "Restore Visas"),
    (PERM_VISAS_SUBMIT, "Submit Visas"),
    (PERM_VISAS_PROCESS, "Process Visas"),
    (PERM_VISAS_APPROVE, "Approve Visas"),
    (PERM_VISAS_REJECT, "Reject Visas"),
    (PERM_PAYMENTS_VIEW, "View Payments"),
    (PERM_PAYMENTS_ADD, "Add Payments"),
    (PERM_PAYMENTS_CHANGE, "Change Payments"),
    (PERM_PAYMENTS_DELETE, "Delete Payments"),
    (PERM_INVOICES_VIEW, "View Invoices"),
    (PERM_INVOICES_ADD, "Add Invoices"),
    (PERM_INVOICES_CHANGE, "Change Invoices"),
    (PERM_INVOICES_DELETE, "Delete Invoices"),
    (PERM_AGENTS_VIEW, "View Agents"),
    (PERM_AGENTS_ADD, "Add Agents"),
    (PERM_AGENTS_CHANGE, "Change Agents"),
    (PERM_AGENTS_DELETE, "Delete Agents"),
    (PERM_PARTNERS_VIEW, "View Partners"),
    (PERM_PARTNERS_ADD, "Add Partners"),
    (PERM_PARTNERS_CHANGE, "Change Partners"),
    (PERM_PARTNERS_DELETE, "Delete Partners"),
    (PERM_SETTINGS_MANAGE, "Manage Settings"),
    (PERM_HRM_VIEW, "View HRM"),
    (PERM_HRM_ADD, "Add HRM"),
    (PERM_HRM_CHANGE, "Change HRM"),
    (PERM_HRM_DELETE, "Delete HRM"),
    (PERM_RECRUITMENT_VIEW, "View Recruitment"),
    (PERM_RECRUITMENT_ADD, "Add Recruitment"),
    (PERM_RECRUITMENT_CHANGE, "Change Recruitment"),
    (PERM_RECRUITMENT_DELETE, "Delete Recruitment"),
    (PERM_WORKVISA_VIEW, "View Work Visa"),
    (PERM_WORKVISA_ADD, "Add Work Visa"),
    (PERM_WORKVISA_CHANGE, "Change Work Visa"),
    (PERM_WORKVISA_DELETE, "Delete Work Visa"),
    (PERM_WHATSAPP_VIEW, "View WhatsApp"),
    (PERM_WHATSAPP_ADD, "Add WhatsApp"),
    (PERM_WHATSAPP_CHANGE, "Change WhatsApp"),
    (PERM_WHATSAPP_DELETE, "Delete WhatsApp"),
    (PERM_REPORTS_VIEW, "View Reports"),
    (PERM_REPORTS_ADD, "Add Reports"),
    (PERM_REPORTS_CHANGE, "Change Reports"),
    (PERM_REPORTS_DELETE, "Delete Reports"),
    (PERM_NOTIFICATIONS_VIEW, "View Notifications"),
    (PERM_NOTIFICATIONS_ADD, "Add Notifications"),
    (PERM_NOTIFICATIONS_CHANGE, "Change Notifications"),
    (PERM_NOTIFICATIONS_DELETE, "Delete Notifications"),
    (PERM_CLIENTPORTAL_VIEW, "View Client Portal"),
    (PERM_CLIENTPORTAL_ADD, "Add Client Portal"),
    (PERM_CLIENTPORTAL_CHANGE, "Change Client Portal"),
    (PERM_CLIENTPORTAL_DELETE, "Delete Client Portal"),
]

ROLE_PERMISSIONS = {
    ROLE_ADMIN: [code for code, _ in ALL_PERMISSIONS],
    ROLE_MANAGER: [
        PERM_DASHBOARD_VIEW,
        PERM_LEADS_VIEW,
        PERM_LEADS_ADD,
        PERM_LEADS_CHANGE,
        PERM_LEADS_DELETE,
        PERM_LEADS_CONVERT,
        PERM_LEADS_ASSIGN,
        PERM_LEADS_IMPORT,
        PERM_LEADS_QUALIFY,
        PERM_LEADS_ASSIGN_COUNSELLOR,
        PERM_FOLLOWUPS_VIEW,
        PERM_FOLLOWUPS_ADD,
        PERM_FOLLOWUPS_CHANGE,
        PERM_FOLLOWUPS_DELETE,
        PERM_TASKS_VIEW,
        PERM_TASKS_ADD,
        PERM_TASKS_CHANGE,
        PERM_TASKS_DELETE,
        PERM_COMMUNICATIONS_VIEW,
        PERM_COMMUNICATIONS_ADD,
        PERM_COMMUNICATIONS_CHANGE,
        PERM_CALLLOGS_VIEW,
        PERM_CALLLOGS_ADD,
        PERM_CALLLOGS_CHANGE,
        PERM_CALLLOGS_DELETE,
        PERM_STUDENTS_VIEW,
        PERM_STUDENTS_ADD,
        PERM_STUDENTS_CHANGE,
        PERM_STUDENTS_DELETE,
        PERM_APPLICATIONS_VIEW,
        PERM_APPLICATIONS_ADD,
        PERM_APPLICATIONS_CHANGE,
        PERM_APPLICATIONS_DELETE,
        PERM_UNIVERSITIES_VIEW,
        PERM_PARTNERS_VIEW,
        PERM_AGENTS_VIEW,
        PERM_DOCUMENTS_VIEW,
        PERM_DOCUMENTS_ADD,
        PERM_DOCUMENTS_CHANGE,
        PERM_DOCUMENTS_DELETE,
        PERM_OFFERLETTERS_VIEW,
        PERM_OFFERLETTERS_ADD,
        PERM_OFFERLETTERS_CHANGE,
        PERM_OFFERLETTERS_DELETE,
        PERM_VISAS_VIEW,
        PERM_REPORTS_VIEW,
    ],
    ROLE_COUNSELLOR: [
        PERM_DASHBOARD_VIEW,
        PERM_LEADS_VIEW,
        PERM_LEADS_ADD,
        PERM_LEADS_CHANGE,
        PERM_LEADS_CONVERT,
        PERM_LEADS_QUALIFY,
        PERM_FOLLOWUPS_VIEW,
        PERM_FOLLOWUPS_ADD,
        PERM_FOLLOWUPS_CHANGE,
        PERM_TASKS_VIEW,
        PERM_TASKS_ADD,
        PERM_TASKS_CHANGE,
        PERM_COMMUNICATIONS_VIEW,
        PERM_COMMUNICATIONS_ADD,
        PERM_WHATSAPP_VIEW,
        PERM_WHATSAPP_ADD,
        PERM_CALLLOGS_VIEW,
        PERM_CALLLOGS_ADD,
        PERM_STUDENTS_VIEW,
        PERM_STUDENTS_ADD,
        PERM_STUDENTS_CHANGE,
        PERM_APPLICATIONS_VIEW,
        PERM_APPLICATIONS_ADD,
        PERM_APPLICATIONS_CHANGE,
        PERM_UNIVERSITIES_VIEW,
        PERM_PARTNERS_VIEW,
        PERM_DOCUMENTS_VIEW,
        PERM_DOCUMENTS_ADD,
        PERM_DOCUMENTS_CHANGE,
        PERM_OFFERLETTERS_VIEW,
        PERM_OFFERLETTERS_ADD,
        PERM_OFFERLETTERS_CHANGE,
        PERM_VISAS_VIEW,
        PERM_VISAS_ADD,
        PERM_VISAS_CHANGE,
        PERM_VISAS_SUBMIT,
    ],
    ROLE_VISA_TEAM: [
        PERM_DASHBOARD_VIEW,
        PERM_STUDENTS_VIEW,
        PERM_APPLICATIONS_VIEW,
        PERM_DOCUMENTS_VIEW,
        PERM_OFFERLETTERS_VIEW,
        PERM_VISAS_VIEW,
        PERM_VISAS_CHANGE,
        PERM_VISAS_PROCESS,
        PERM_VISAS_APPROVE,
        PERM_VISAS_REJECT,
        PERM_TASKS_VIEW,
        PERM_TASKS_ADD,
        PERM_TASKS_CHANGE,
    ],
    ROLE_TELECALLER: [
        PERM_DASHBOARD_VIEW,
        PERM_LEADS_VIEW,
        PERM_LEADS_ADD,
        PERM_LEADS_CHANGE,
        PERM_FOLLOWUPS_VIEW,
        PERM_FOLLOWUPS_ADD,
        PERM_FOLLOWUPS_CHANGE,
        PERM_TASKS_VIEW,
        PERM_TASKS_ADD,
        PERM_TASKS_CHANGE,
        PERM_COMMUNICATIONS_VIEW,
        PERM_COMMUNICATIONS_ADD,
        PERM_WHATSAPP_VIEW,
        PERM_WHATSAPP_ADD,
        PERM_CALLLOGS_VIEW,
        PERM_CALLLOGS_ADD,
        PERM_DOCUMENTS_VIEW,
        PERM_DOCUMENTS_ADD,
        PERM_UNIVERSITIES_VIEW,
    ],
    ROLE_FINANCE: [
        PERM_DASHBOARD_VIEW,
        PERM_STUDENTS_VIEW,
        PERM_APPLICATIONS_VIEW,
        PERM_PAYMENTS_VIEW,
        PERM_INVOICES_VIEW,
    ],
    ROLE_VIEWER: [
        PERM_DASHBOARD_VIEW,
        PERM_LEADS_VIEW,
        PERM_FOLLOWUPS_VIEW,
        PERM_TASKS_VIEW,
        PERM_COMMUNICATIONS_VIEW,
        PERM_CALLLOGS_VIEW,
        PERM_STUDENTS_VIEW,
        PERM_APPLICATIONS_VIEW,
        PERM_UNIVERSITIES_VIEW,
        PERM_PARTNERS_VIEW,
        PERM_DOCUMENTS_VIEW,
    ],
}
