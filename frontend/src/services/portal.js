import axios from "axios";

import { API_BASE_URL } from "../config/api";

const portalApi = axios.create({
    baseURL: API_BASE_URL,
});

portalApi.interceptors.request.use((config) => {
    const token = localStorage.getItem("portal_token");

    if (token) {
        config.headers["X-Portal-Token"] = token;
    }

    return config;
});

export async function portalLogin(username, password) {
    const response = await portalApi.post("/portal/login/", {
        username,
        password,
    });
    return response.data;
}

export async function getPortalProfile() {
    const response = await portalApi.get("/portal/me/");
    return response.data;
}

export async function getPortalDocuments() {
    const response = await portalApi.get("/portal/documents/");
    return response.data;
}

export async function uploadPortalDocument(id, file) {
    const formData = new FormData();
    formData.append("file", file);

    const response = await portalApi.post(
        `/portal/documents/${id}/upload/`,
        formData,
    );

    return response.data;
}

export async function getPortalApplications() {
    const response = await portalApi.get("/portal/applications/");
    return response.data;
}

export async function getPortalOffers() {
    const response = await portalApi.get("/portal/offers/");
    return response.data;
}

export async function getPortalVisaCases() {
    const response = await portalApi.get("/portal/visa-cases/");
    return response.data;
}

export async function getPortalTimeline() {
    const response = await portalApi.get("/portal/timeline/");
    return response.data;
}

export default portalApi;
