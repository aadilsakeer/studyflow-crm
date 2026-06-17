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