import api from "./api";

export async function login(
    username,
    password
) {
    const response = await api.post(
        "/token/",
        {
            username,
            password,
        }
    );

    return response.data;
}

export async function getCurrentUser() {
    const response = await api.get("/me/");

    return response.data;
}

export async function logout() {
    const refresh = localStorage.getItem("refresh");

    if (!refresh) {
        return;
    }

    try {
        await api.post("/token/blacklist/", {
            refresh,
        });
    } catch (error) {
        if (error.response?.status !== 401) {
            throw error;
        }
    }
}