import api from "./api";

export async function getTasks(params = {}) {
    const response = await api.get("/tasks/", { params });
    return response.data;
}

export async function getTask(id) {
    const response = await api.get(`/tasks/${id}/`);
    return response.data;
}

export async function createTask(payload) {
    const response = await api.post("/tasks/", payload);
    return response.data;
}

export async function updateTask(id, payload) {
    const response = await api.patch(`/tasks/${id}/`, payload);
    return response.data;
}

export async function deleteTask(id) {
    await api.delete(`/tasks/${id}/`);
}

export async function getTaskSummary() {
    const response = await api.get("/tasks/summary/");
    return response.data;
}

export const TASK_TYPES = [
    { value: "follow_up_call", label: "Follow-up Call" },
    { value: "document_collection", label: "Document Collection" },
    {
        value: "application_submission",
        label: "Application Submission",
    },
    { value: "offer_review", label: "Offer Review" },
    { value: "visa_appointment", label: "Visa Appointment" },
    { value: "general_task", label: "General Task" },
];

export const TASK_STATUSES = [
    { value: "pending", label: "Pending" },
    { value: "in_progress", label: "In Progress" },
    { value: "completed", label: "Completed" },
    { value: "cancelled", label: "Cancelled" },
];

export const TASK_PRIORITIES = [
    { value: "low", label: "Low" },
    { value: "medium", label: "Medium" },
    { value: "high", label: "High" },
    { value: "urgent", label: "Urgent" },
];
