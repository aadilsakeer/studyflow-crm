import api from "./api";

export async function getStudents(params = {}) {
    const response = await api.get("/students/", {
        params,
    });
    return response.data;
}

export async function getStudent(id) {
    const response = await api.get(
        `/students/${id}/`
    );
    return response.data;
}

export async function updateStudent(id, data) {
    const response = await api.patch(
        `/students/${id}/`,
        data
    );
    return response.data;
}
