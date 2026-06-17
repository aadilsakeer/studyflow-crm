import { useEffect, useState, useRef } from "react";
import api from "../services/api";
import { showError } from "../utils/toast";
import { formatApiError } from "../services/leads";
import {
    DASHBOARD_RANGE_KEY,
    DEFAULT_DASHBOARD_RANGE,
} from "../utils/dashboardRanges";

const EMPTY_DASHBOARD = {
    total_leads: 0,
    total_students: 0,
    total_applications: 0,
    total_revenue: 0,
    todays_follow_ups: 0,
    pending_follow_ups: 0,
    completed_today: 0,
    kpis: {},
    trends: {},
    lead_trend: [],
    recent_activities: [],
    range: DEFAULT_DASHBOARD_RANGE,
    range_label: "Last 30 Days",
};

function readStoredRange() {
    const stored = localStorage.getItem(
        DASHBOARD_RANGE_KEY,
    );

    return stored || DEFAULT_DASHBOARD_RANGE;
}

function useDashboard() {
    const [range, setRange] = useState(
        readStoredRange,
    );
    const [dashboard, setDashboard] = useState(
        EMPTY_DASHBOARD,
    );
    const [loading, setLoading] = useState(true);
    const errorShown = useRef(false);

    useEffect(() => {
        loadDashboard(range);

        return () => {
            errorShown.current = false;
        };
    }, [range]);

    async function loadDashboard(selectedRange) {
        setLoading(true);

        try {
            const response = await api.get(
                "/dashboard/",
                {
                    params: {
                        range: selectedRange,
                    },
                },
            );

            setDashboard({
                ...EMPTY_DASHBOARD,
                ...response.data,
                recent_activities:
                    response.data.recent_activities
                    ?? [],
            });
        } catch (error) {
            console.error(
                "Error loading dashboard:",
                error,
            );

            setDashboard(EMPTY_DASHBOARD);

            if (!errorShown.current) {
                errorShown.current = true;
                showError(
                    formatApiError(error)
                    || "Failed to load dashboard",
                );
            }
        } finally {
            setLoading(false);
        }
    }

    function updateRange(nextRange) {
        localStorage.setItem(
            DASHBOARD_RANGE_KEY,
            nextRange,
        );
        setRange(nextRange);
    }

    return {
        dashboard,
        loading,
        range,
        setRange: updateRange,
    };
}

export default useDashboard;
