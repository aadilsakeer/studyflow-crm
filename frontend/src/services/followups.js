import api from "./api";

export async function getFollowUps(params = {}) {
    const response = await api.get("/followups/", {
        params,
    });
    return response.data;
}

export async function createFollowUp(data) {
    const response = await api.post("/followups/", data);
    return response.data;
}

export async function updateFollowUp(id, data) {
    const response = await api.patch(
        `/followups/${id}/`,
        data
    );
    return response.data;
}

export async function getLeadFollowUps(leadId) {
    return getFollowUps({ lead: leadId });
}
