import toast from "react-hot-toast";

export function showSuccess(message) {
    toast.success(message);
}

export function showError(message) {
    toast.error(message);
}

export function showInfo(message) {
    toast(message);
}
