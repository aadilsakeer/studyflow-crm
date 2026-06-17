export function createPermissionHelpers(
    permissions = []
) {
    const set = new Set(permissions);

    function can(code) {
        return set.has(code);
    }

    function canAny(codes) {
        return codes.some((code) => set.has(code));
    }

    function canAll(codes) {
        return codes.every((code) => set.has(code));
    }

    return { can, canAny, canAll };
}

export const NAV_PERMISSIONS = {
    "/": "dashboard.view",
    "/leads": "leads.view",
    "/follow-ups": "followups.view",
    "/students": "students.view",
    "/applications": "applications.view",
    "/universities": "universities.view",
};
