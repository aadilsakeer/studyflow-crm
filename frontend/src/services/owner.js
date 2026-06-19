import api from "./api";

const BASE = "/owner";

export const getOwnerDashboard = () => api.get(`${BASE}/dashboard/`);
export const getOwnerCompanies = () => api.get(`${BASE}/companies/`);
export const createOwnerCompany = (payload) => api.post(`${BASE}/companies/`, payload);
export const ownerOnboardTenant = (payload) => api.post(`${BASE}/onboard/`, payload);
export const ownerUserAction = (userId, payload) =>
    api.post(`${BASE}/users/${userId}/`, payload);
export const getOwnerCompany = (id) => api.get(`${BASE}/companies/${id}/`);
export const ownerCompanyAction = (id, payload) =>
    api.patch(`${BASE}/companies/${id}/`, payload);
export const deleteOwnerCompany = (id) => api.delete(`${BASE}/companies/${id}/`);
export const ownerImpersonate = (id, userId) =>
    api.post(`${BASE}/companies/${id}/impersonate/`, userId ? { user_id: userId } : {});

export const getOwnerModuleCatalog = () => api.get(`${BASE}/modules/`);
export const getOwnerCompanyModules = (id) => api.get(`${BASE}/companies/${id}/modules/`);
export const ownerModuleAction = (id, payload) =>
    api.post(`${BASE}/companies/${id}/modules/`, payload);
export const ownerBulkModuleAssign = (payload) =>
    api.post(`${BASE}/modules/bulk-assign/`, payload);

export function startImpersonation(tokens) {
    localStorage.setItem("owner_access", localStorage.getItem("access"));
    localStorage.setItem("owner_refresh", localStorage.getItem("refresh"));
    localStorage.setItem("access", tokens.access);
    localStorage.setItem("refresh", tokens.refresh);
    localStorage.setItem("impersonating", "1");
    window.location.href = "/";
}

export function returnToOwner() {
    const access = localStorage.getItem("owner_access");
    const refresh = localStorage.getItem("owner_refresh");
    if (access) localStorage.setItem("access", access);
    if (refresh) localStorage.setItem("refresh", refresh);
    localStorage.removeItem("owner_access");
    localStorage.removeItem("owner_refresh");
    localStorage.removeItem("impersonating");
    window.location.href = "/owner";
}
