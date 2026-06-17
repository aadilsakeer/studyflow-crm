import api from "./api";

export async function getCallLogs(params = {}) {
    const response = await api.get("/calllogs/", {
        params,
    });
    return response.data;
}

export async function createCallLog(data) {
    const response = await api.post(
        "/calllogs/",
        data
    );
    return response.data;
}

export async function getLeadCallLogs(leadId) {
    return getCallLogs({ lead: leadId });
}
