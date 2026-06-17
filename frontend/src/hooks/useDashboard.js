import { useEffect, useState, useRef } from "react";
import api from "../services/api";
import { showError } from "../utils/toast";
import { formatApiError } from "../services/leads";

function buildEmptyTrend() {
    const trend = [];
    const today = new Date();

    for (let i = 5; i >= 0; i -= 1) {
        const date = new Date(
            today.getFullYear(),
            today.getMonth() - i,
            1,
        );

        trend.push({
            month: date.toLocaleString(
                "en-US",
                { month: "short" },
            ),
            leads: 0,
        });
    }

    return trend;
}

const EMPTY_DASHBOARD = {
    total_leads: 0,
    total_students: 0,
    total_applications: 0,
    total_revenue: 0,
    todays_follow_ups: 0,
    pending_follow_ups: 0,
    completed_today: 0,
    lead_trend: buildEmptyTrend(),
    recent_activities: [],
};

function useDashboard() {
    const [dashboard, setDashboard] = useState(
        EMPTY_DASHBOARD
    );
    const [loading, setLoading] = useState(true);
    const errorShown = useRef(false);

    useEffect(() => {
        loadDashboard();

        return () => {
            errorShown.current = false;
        };
    }, []);

    async function loadDashboard() {
        try {
            const response = await api.get(
                "/dashboard/"
            );

            setDashboard({
                ...EMPTY_DASHBOARD,
                ...response.data,
                lead_trend:
                    response.data.lead_trend?.length
                        ? response.data.lead_trend
                        : buildEmptyTrend(),
                recent_activities:
                    response.data.recent_activities
                    ?? [],
            });
        } catch (error) {
            console.error(
                "Error loading dashboard:",
                error
            );

            setDashboard(EMPTY_DASHBOARD);

            if (!errorShown.current) {
                errorShown.current = true;
                showError(
                    formatApiError(error)
                    || "Failed to load dashboard"
                );
            }
        } finally {
            setLoading(false);
        }
    }

    return {
        dashboard,
        loading,
    };
}

export default useDashboard;
