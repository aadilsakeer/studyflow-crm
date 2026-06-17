import {
    Paper,
    ToggleButton,
    ToggleButtonGroup,
    Typography,
    Box,
} from "@mui/material";

import {
    DASHBOARD_RANGES,
} from "../utils/dashboardRanges";

function DashboardRangeSelector({
    value,
    onChange,
    label,
}) {
    return (
        <Paper
            elevation={0}
            sx={{
                p: 1.5,
                borderRadius: 3,
                border: "1px solid #E5E7EB",
                backgroundColor: "#FFFFFF",
                mb: 3,
            }}
        >
            <Box
                sx={{
                    display: "flex",
                    flexWrap: "wrap",
                    alignItems: "center",
                    gap: 2,
                    justifyContent: "space-between",
                }}
            >
                <Typography
                    variant="body2"
                    color="text.secondary"
                    fontWeight={600}
                >
                    {label || "Time Range"}
                </Typography>

                <ToggleButtonGroup
                    exclusive
                    size="small"
                    value={value}
                    onChange={(_, next) => {
                        if (next) {
                            onChange(next);
                        }
                    }}
                    sx={{
                        flexWrap: "wrap",
                        gap: 0.5,
                    }}
                >
                    {DASHBOARD_RANGES.map(
                        (option) => (
                            <ToggleButton
                                key={option.value}
                                value={option.value}
                                sx={{
                                    textTransform: "none",
                                    px: 1.5,
                                }}
                            >
                                {option.label}
                            </ToggleButton>
                        ),
                    )}
                </ToggleButtonGroup>
            </Box>
        </Paper>
    );
}

export default DashboardRangeSelector;
