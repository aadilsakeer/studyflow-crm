import api from "./api";

export async function getWhatsAppServer() {
    const response = await api.get("/whatsapp/server/");
    return response.data;
}

export async function updateWhatsAppServer(data) {
    const response = await api.patch("/whatsapp/server/", data);
    return response.data;
}

export async function getWhatsAppSessionStatus() {
    const response = await api.get("/whatsapp/session/status/");
    return response.data;
}

export async function connectWhatsAppSession(phoneNumber = "") {
    const response = await api.post("/whatsapp/session/connect/", {
        phone_number: phoneNumber,
    });
    return response.data;
}

export async function getWhatsAppQR() {
    const response = await api.get("/whatsapp/session/qr/");
    return response.data;
}

export async function sendWhatsAppMessage(data) {
    const response = await api.post("/whatsapp/send/", data);
    return response.data;
}

export async function getWhatsAppMessages() {
    const response = await api.get("/whatsapp/messages/");
    return response.data;
}
