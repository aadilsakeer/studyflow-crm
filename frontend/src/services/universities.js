import api from "./api";

export async function getUniversities(params = {}) {
    const response = await api.get(
        "/universities/",
        { params }
    );
    return response.data;
}

export async function createUniversity(data) {
    const response = await api.post(
        "/universities/",
        data
    );
    return response.data;
}

export async function getCourses(params = {}) {
    const response = await api.get(
        "/courses/",
        { params }
    );
    return response.data;
}
