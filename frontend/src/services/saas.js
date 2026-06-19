import api from "./api";

const BASE = "/saas";

export const getPlans = () => api.get(`${BASE}/plans/`);

export const registerTenant = (payload) =>
    api.post(`${BASE}/onboard/register/`, payload);

export const advanceOnboarding = (step) =>
    api.post(`${BASE}/onboard/step/`, { step });

export const getSubscription = () => api.get(`${BASE}/subscription/`);

export const getUsage = () => api.get(`${BASE}/usage/`);

export const getSettings = () => api.get(`${BASE}/settings/`);

export const updateSettings = (payload) =>
    api.patch(`${BASE}/settings/`, payload);

export const uploadBranding = (formData) =>
    api.post(`${BASE}/settings/branding/`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
    });

export const getInvoices = () => api.get(`${BASE}/billing/invoices/`);

export const getPayments = () => api.get(`${BASE}/billing/payments/`);

export const startCheckout = (payload) =>
    api.post(`${BASE}/billing/checkout/`, payload);

export const openBillingPortal = () =>
    api.post(`${BASE}/billing/portal/`);

export const changePlan = (planCode) =>
    api.post(`${BASE}/subscription/change-plan/`, { plan_code: planCode });

export const getAdminDashboard = () => api.get(`${BASE}/admin/dashboard/`);

export const getProductionOps = () => api.get("/health/operations/");
export const postProductionOps = (payload) => api.post("/health/operations/", payload);

export const getAdminOperations = () => api.get(`${BASE}/admin/operations/`);
export const adminTenantAction = (id, action) =>
    api.patch(`${BASE}/admin/tenants/${id}/`, { action });
export const adminChangePlan = (id, planCode) =>
    api.post(`${BASE}/admin/tenants/${id}/plan/`, { plan_code: planCode });
export const adminExtendTrial = (id, days = 7) =>
    api.post(`${BASE}/admin/tenants/${id}/extend-trial/`, { days });
export const adminResetUsage = (id) =>
    api.post(`${BASE}/admin/tenants/${id}/reset-usage/`);
export const adminTicketOps = (id, payload) =>
    api.patch(`${BASE}/admin/support/tickets/${id}/ops/`, payload);
export const adminImpersonate = (userId) =>
    api.post(`${BASE}/admin/impersonate/${userId}/`);
export const adminTenantActivity = (id) =>
    api.get(`${BASE}/admin/tenants/${id}/activity/`);

export const getAdminSupportTickets = () =>
    api.get(`${BASE}/admin/support/tickets/`);

export const getSupportTickets = () => api.get(`${BASE}/support/tickets/`);

export const createSupportTicket = (payload) =>
    api.post(`${BASE}/support/tickets/`, payload);

export const getSupportTicket = (id) =>
    api.get(`${BASE}/support/tickets/${id}/`);

export const updateSupportTicket = (id, payload) =>
    api.patch(`${BASE}/support/tickets/${id}/`, payload);

export const addTicketMessage = (id, payload) =>
    api.post(`${BASE}/support/tickets/${id}/messages/`, payload);

export const uploadTicketAttachment = (id, file) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.post(`${BASE}/support/tickets/${id}/attachments/`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
    });
};

export const cancelSubscription = () => api.post(`${BASE}/subscription/cancel/`);
export const downgradePlan = (planCode) =>
    api.post(`${BASE}/subscription/downgrade/`, { plan_code: planCode });
export const getPublicBranding = (email) =>
    api.get(`${BASE}/branding/public/`, { params: email ? { email } : {} });
