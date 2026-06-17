import api from "./api";

export async function getApplications(params = {}) {
    const response = await api.get(
        "/applications/",
        { params }
    );
    return response.data;
}

export async function createApplication(data) {
    const response = await api.post(
        "/applications/",
        data
    );
    return response.data;
}

export async function updateApplication(id, data) {
    const response = await api.patch(
        `/applications/${id}/`,
        data
    );
    return response.data;
}

export async function deleteApplication(id) {
    return api.delete(
        `/applications/${id}/`
    );
}

export async function getStudentApplications(
    studentId
) {
    return getApplications({
        student: studentId,
    });
}
