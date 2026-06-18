import api from "./api";

export async function getAdvancedReports(range = "30d") {
    const response = await api.get("/reports/advanced/", {
        params: { range },
    });
    return response.data;
}

export async function downloadAdvancedReport(
    format,
    range = "30d",
) {
    const response = await api.get("/reports/advanced/export/", {
        params: { format, range },
        responseType: "blob",
    });

    const blob = new Blob([response.data]);
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `advanced-report.${format === "xlsx" ? "xlsx" : "csv"}`;
    link.click();
    window.URL.revokeObjectURL(url);
}
