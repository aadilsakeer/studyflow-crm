import api from "./api";

export async function getLeadTimeline(leadId) {
    const response = await api.get(
        `/leads/${leadId}/timeline/`
    );
    return response.data;
}
