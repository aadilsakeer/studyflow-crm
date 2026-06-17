import axios from "axios";

import { API_BASE_URL } from "../config/api";

const api = axios.create({
    baseURL: API_BASE_URL,
});

let isRefreshing = false;
let failedQueue = [];

function processQueue(error, token = null) {
    failedQueue.forEach(({ resolve, reject }) => {
        if (error) {
            reject(error);
        } else {
            resolve(token);
        }
    });

    failedQueue = [];
}

api.interceptors.request.use((config) => {
    const token = localStorage.getItem("access");

    if (token) {
        config.headers.Authorization =
            `Bearer ${token}`;
    }

    return config;
});

api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        if (
            error.response?.status !== 401
            || originalRequest._retry
            || originalRequest.url?.includes(
                "/token/"
            )
        ) {
            return Promise.reject(error);
        }

        if (isRefreshing) {
            return new Promise((resolve, reject) => {
                failedQueue.push({
                    resolve,
                    reject,
                });
            }).then((token) => {
                originalRequest.headers.Authorization =
                    `Bearer ${token}`;
                return api(originalRequest);
            });
        }

        originalRequest._retry = true;
        isRefreshing = true;

        const refresh = localStorage.getItem(
            "refresh"
        );

        if (!refresh) {
            processQueue(error, null);
            isRefreshing = false;
            localStorage.removeItem("username");
            window.dispatchEvent(
                new Event("auth:logout")
            );
            return Promise.reject(error);
        }

        try {
            const response = await axios.post(
                `${API_BASE_URL}/token/refresh/`,
                { refresh }
            );

            const newAccess = response.data.access;

            localStorage.setItem(
                "access",
                newAccess
            );

            if (response.data.refresh) {
                localStorage.setItem(
                    "refresh",
                    response.data.refresh
                );
            }

            processQueue(null, newAccess);

            originalRequest.headers.Authorization =
                `Bearer ${newAccess}`;

            return api(originalRequest);
        } catch (refreshError) {
            processQueue(refreshError, null);
            localStorage.removeItem("access");
            localStorage.removeItem("refresh");
            localStorage.removeItem("username");
            window.dispatchEvent(
                new Event("auth:logout")
            );
            return Promise.reject(refreshError);
        } finally {
            isRefreshing = false;
        }
    }
);

export default api;
