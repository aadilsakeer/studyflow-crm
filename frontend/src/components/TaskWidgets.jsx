import { useNavigate } from "react-router-dom";

import {
    Paper,
    Typography,
    Box,
} from "@mui/material";

import Grid from "@mui/material/Grid";

import CalendarTodayIcon from "@mui/icons-material/CalendarToday";
import PendingActionsIcon from "@mui/icons-material/PendingActions";
import WarningIcon from "@mui/icons-material/Warning";
import NotificationsActiveIcon from "@mui/icons-material/NotificationsActive";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";

function TaskWidgets({ dashboard }) {
    const navigate = useNavigate();

    const widgets = [
        {
            title: "Today's Tasks",
            value: dashboard?.todays_tasks ?? 0,
            icon: <CalendarTodayIcon />,
            color: "#2563EB",
            filter: "due_today",
        },
        {
            title: "Pending Tasks",
            value: dashboard?.pending_tasks ?? 0,
            icon: <PendingActionsIcon />,
            color: "#F59E0B",
            filter: "pending",
        },
        {
            title: "Overdue",
            value: dashboard?.overdue_tasks ?? 0,
            icon: <WarningIcon />,
            color: "#DC2626",
            filter: "overdue",
        },
        {
            title: "Reminders Due",
            value: dashboard?.due_reminders ?? 0,
            icon: <NotificationsActiveIcon />,
            color: "#7C3AED",
            filter: "reminder_due",
        },
        {
            title: "Completed Today",
            value: dashboard?.completed_today_tasks ?? 0,
            icon: <CheckCircleIcon />,
            color: "#10B981",
            filter: "completed_today",
        },
    ];

    return (
        <Grid container spacing={3} sx={{ mt: 1 }}>
            {widgets.map((widget) => (
                <Grid
                    size={{ xs: 12, sm: 6, md: 4, lg: 2.4 }}
                    key={widget.title}
                >
                    <Paper
                        elevation={0}
                        onClick={() =>
                            navigate(
                                `/tasks?filter=${widget.filter}`,
                            )
                        }
                        sx={{
                            p: 3,
                            borderRadius: 4,
                            border: "1px solid #E5E7EB",
                            cursor: "pointer",
                        }}
                    >
                        <Box
                            sx={{
                                display: "flex",
                                justifyContent: "space-between",
                            }}
                        >
                            <Typography
                                variant="body2"
                                color="text.secondary"
                            >
                                {widget.title}
                            </Typography>
                            <Box sx={{ color: widget.color }}>
                                {widget.icon}
                            </Box>
                        </Box>
                        <Typography
                            variant="h5"
                            fontWeight={700}
                            sx={{ mt: 2 }}
                        >
                            {widget.value}
                        </Typography>
                    </Paper>
                </Grid>
            ))}
        </Grid>
    );
}

export default TaskWidgets;
