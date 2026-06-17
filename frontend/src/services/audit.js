import api from "./api";

export async function getLeadAuditLogs(leadId) {
    const response = await api.get(
        `/leads/${leadId}/audit/`
    );
    return response.data;
}
