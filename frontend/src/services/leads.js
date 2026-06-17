import api from "./api";

export async function getLeads(params = {}) {
    const response = await api.get("/leads/", {
        params,
    });
    return response.data;
}

export async function createLead(data) {
    const response = await api.post("/leads/", data);
    return response.data;
}

export async function updateLead(id, data) {
    const response = await api.patch(`/leads/${id}/`, data);
    return response.data;
}

export async function deleteLead(id) {
    return api.delete(`/leads/${id}/`);
}

export async function convertLead(id) {
    const response = await api.post(
        `/leads/${id}/convert/`
    );
    return response.data;
}

export function formatApiError(error) {
    const data = error.response?.data;

    if (!data) {
        return error.message || "Request failed";
    }

    if (typeof data === "string") {
        return data;
    }

    if (data.detail) {
        return data.detail;
    }

    return Object.entries(data)
        .map(([field, messages]) => {
            const text = Array.isArray(messages)
                ? messages.join(", ")
                : String(messages);
            return `${field}: ${text}`;
        })
        .join("\n");
}
