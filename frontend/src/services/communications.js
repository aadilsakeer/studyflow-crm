import api from "./api";

export async function getCommunicationHistory(params = {}) {
    const response = await api.get("/communications/history/", {
        params,
    });
    return response.data;
}

export async function getCommunicationNotes(params = {}) {
    const response = await api.get("/communications/notes/", {
        params,
    });
    return response.data;
}

export async function createCommunicationNote(data) {
    const response = await api.post(
        "/communications/notes/",
        data,
    );
    return response.data;
}

export async function createEmailLog(data) {
    const response = await api.post(
        "/communications/emails/",
        data,
    );
    return response.data;
}

export async function createWhatsAppLog(data) {
    const response = await api.post(
        "/communications/whatsapp-logs/",
        data,
    );
    return response.data;
}
