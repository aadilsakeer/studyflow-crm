import {
    Paper,
    Typography,
    Box,
} from "@mui/material";

import {
    ResponsiveContainer,
    LineChart,
    Line,
    XAxis,
    YAxis,
    Tooltip,
    CartesianGrid,
} from "recharts";

function DashboardChart({ trend = [] }) {
    const hasTrend = trend.length > 0;

    return (
        <Paper
            elevation={0}
            sx={{
                p: 3,
                borderRadius: 4,
                border: "1px solid #E5E7EB",
                backgroundColor: "#FFFFFF",
                height: "100%",
                minHeight: 420,
            }}
        >
            <Typography
                variant="h6"
                sx={{
                    mb: 1,
                    fontWeight: 600,
                }}
            >
                Lead Trend
            </Typography>

            <Typography
                variant="body2"
                color="text.secondary"
                sx={{ mb: 3 }}
            >
                New leads over the last 6 months
            </Typography>

            {!hasTrend ? (
                <Box
                    sx={{
                        height: 300,
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                    }}
                >
                    <Typography
                        color="text.secondary"
                    >
                        No lead data yet. Create
                        your first lead to see
                        trends.
                    </Typography>
                </Box>
            ) : (
                <ResponsiveContainer
                    width="100%"
                    height={300}
                >
                    <LineChart data={trend}>
                        <CartesianGrid
                            strokeDasharray="3 3"
                            stroke="#F1F5F9"
                        />

                        <XAxis
                            dataKey="month"
                            tick={{ fill: "#64748B" }}
                        />

                        <YAxis
                            allowDecimals={false}
                            tick={{ fill: "#64748B" }}
                        />

                        <Tooltip
                            formatter={(value) => [
                                value,
                                "Leads",
                            ]}
                        />

                        <Line
                            type="monotone"
                            dataKey="leads"
                            stroke="#2563EB"
                            strokeWidth={3}
                            dot={{
                                r: 4,
                                fill: "#2563EB",
                            }}
                            activeDot={{ r: 6 }}
                        />
                    </LineChart>
                </ResponsiveContainer>
            )}
        </Paper>
    );
}

export default DashboardChart;
