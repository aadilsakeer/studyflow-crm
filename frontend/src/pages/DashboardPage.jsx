import DashboardCards from "../components/DashboardCards";
import FollowUpWidgets from "../components/FollowUpWidgets";
import DashboardTrendCharts from "../components/DashboardTrendCharts";
import DashboardRangeSelector from "../components/DashboardRangeSelector";
import RecentActivities from "../components/RecentActivities";
import LoadingState from "../components/LoadingState";

import { Box, Typography } from "@mui/material";

import useDashboard from "../hooks/useDashboard";

function DashboardPage() {
    const {
        dashboard,
        loading,
        range,
        setRange,
    } = useDashboard();

    if (loading) {
        return (
            <LoadingState message="Loading dashboard..." />
        );
    }

    return (
        <>
            <Box sx={{ mb: 3 }}>
                <Typography
                    variant="h4"
                    fontWeight={700}
                >
                    Dashboard
                </Typography>

                <Typography
                    color="text.secondary"
                    sx={{ mt: 0.5 }}
                >
                    Overview of your CRM
                    performance
                </Typography>
            </Box>

            <DashboardRangeSelector
                value={range}
                onChange={setRange}
                label={
                    dashboard?.range_label
                    || "Time Range"
                }
            />

            <DashboardCards
                dashboard={dashboard}
            />

            <FollowUpWidgets
                dashboard={dashboard}
            />

            <Box
                sx={{
                    display: "flex",
                    flexDirection: {
                        xs: "column",
                        lg: "row",
                    },
                    gap: 3,
                    mt: 3,
                }}
            >
                <Box sx={{ flex: 2 }}>
                    <DashboardTrendCharts
                        trends={dashboard?.trends}
                        rangeLabel={
                            dashboard?.range_label
                        }
                    />
                </Box>

                <Box sx={{ flex: 1 }}>
                    <RecentActivities
                        activities={
                            dashboard?.recent_activities
                        }
                    />
                </Box>
            </Box>
        </>
    );
}

export default DashboardPage;
