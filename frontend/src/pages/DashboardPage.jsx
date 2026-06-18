import DashboardCards from "../components/DashboardCards";
import TaskWidgets from "../components/TaskWidgets";
import FollowUpWidgets from "../components/FollowUpWidgets";
import DashboardTrendCharts from "../components/DashboardTrendCharts";
import DashboardRangeSelector from "../components/DashboardRangeSelector";
import DashboardOperationsLinks from "../components/DashboardOperationsLinks";
import TelecallerDashboard from "../components/TelecallerDashboard";
import CounsellorDashboard from "../components/CounsellorDashboard";
import RecentActivities from "../components/RecentActivities";
import LoadingState from "../components/LoadingState";

import { Box, Typography } from "@mui/material";

import useDashboard from "../hooks/useDashboard";
import usePermissions from "../hooks/usePermissions";

function DashboardPage() {
    const { user } = usePermissions();
    const isCounsellor =
        user?.role_name === "Counsellor";
    const {
        dashboard,
        telecallerDashboard,
        counsellorDashboard,
        loading,
        range,
        setRange,
    } = useDashboard();

    const isTelecaller =
        user?.role_name === "Telecaller";

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

            {isCounsellor && (
                <CounsellorDashboard
                    data={counsellorDashboard}
                />
            )}

            {isTelecaller && (
                <TelecallerDashboard
                    data={telecallerDashboard}
                />
            )}

            <DashboardCards
                dashboard={dashboard}
            />

            <DashboardOperationsLinks />

            <TaskWidgets dashboard={dashboard} />

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
