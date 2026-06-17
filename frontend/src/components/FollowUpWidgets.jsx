import { useNavigate } from "react-router-dom";

import {
    Paper,
    Typography,
    Box,
} from "@mui/material";

import Grid from "@mui/material/Grid";

import CalendarTodayIcon from "@mui/icons-material/CalendarToday";
import PendingActionsIcon from "@mui/icons-material/PendingActions";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";

function FollowUpWidgets({ dashboard }) {
    const navigate = useNavigate();

    const widgets = [
        {
            title: "Today's Follow Ups",
            value: dashboard?.todays_follow_ups ?? 0,
            icon: <CalendarTodayIcon />,
            color: "#2563EB",
            filter: "today",
        },
        {
            title: "Pending Follow Ups",
            value: dashboard?.pending_follow_ups ?? 0,
            icon: <PendingActionsIcon />,
            color: "#F59E0B",
            filter: "pending",
        },
        {
            title: "Completed Today",
            value: dashboard?.completed_today ?? 0,
            icon: <CheckCircleIcon />,
            color: "#10B981",
            filter: "completed_today",
        },
    ];

    return (
        <Grid
            container
            spacing={3}
            sx={{ mt: 1 }}
        >
            {widgets.map((widget) => (
                <Grid
                    size={{
                        xs: 12,
                        md: 4,
                    }}
                    key={widget.title}
                >
                    <Paper
                        elevation={0}
                        onClick={() =>
                            navigate(
                                `/follow-ups?filter=${widget.filter}`
                            )
                        }
                        sx={{
                            p: 3,
                            borderRadius: 4,
                            border:
                                "1px solid #E5E7EB",
                            backgroundColor:
                                "#FFFFFF",
                            cursor: "pointer",
                            transition:
                                "box-shadow 0.2s",
                            "&:hover": {
                                boxShadow:
                                    "0 4px 12px rgba(0,0,0,0.08)",
                            },
                        }}
                    >
                        <Box
                            sx={{
                                display: "flex",
                                justifyContent:
                                    "space-between",
                                alignItems:
                                    "center",
                            }}
                        >
                            <Typography
                                variant="body2"
                                color="text.secondary"
                            >
                                {widget.title}
                            </Typography>

                            <Box
                                sx={{
                                    color: widget.color,
                                }}
                            >
                                {widget.icon}
                            </Box>
                        </Box>

                        <Box mt={2}>
                            <Typography
                                variant="h5"
                                fontWeight={700}
                            >
                                {widget.value}
                            </Typography>
                        </Box>
                    </Paper>
                </Grid>
            ))}
        </Grid>
    );
}

export default FollowUpWidgets;
