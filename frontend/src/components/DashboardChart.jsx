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

function DashboardChart({
    title,
    subtitle,
    trend = [],
    dataKey = "value",
    seriesLabel = "Count",
    color = "#2563EB",
    valueFormatter,
}) {
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
                minHeight: 320,
            }}
        >
            <Typography
                variant="h6"
                sx={{
                    mb: 1,
                    fontWeight: 600,
                }}
            >
                {title}
            </Typography>

            {subtitle ? (
                <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{ mb: 3 }}
                >
                    {subtitle}
                </Typography>
            ) : null}

            {!hasTrend ? (
                <Box
                    sx={{
                        height: 240,
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                    }}
                >
                    <Typography
                        color="text.secondary"
                    >
                        No data for this period.
                    </Typography>
                </Box>
            ) : (
                <ResponsiveContainer
                    width="100%"
                    height={240}
                >
                    <LineChart data={trend}>
                        <CartesianGrid
                            strokeDasharray="3 3"
                            stroke="#F1F5F9"
                        />

                        <XAxis
                            dataKey="label"
                            tick={{ fill: "#64748B" }}
                        />

                        <YAxis
                            allowDecimals={false}
                            tick={{ fill: "#64748B" }}
                        />

                        <Tooltip
                            formatter={(value) => [
                                valueFormatter
                                    ? valueFormatter(value)
                                    : value,
                                seriesLabel,
                            ]}
                        />

                        <Line
                            type="monotone"
                            dataKey={dataKey}
                            stroke={color}
                            strokeWidth={3}
                            dot={{
                                r: 4,
                                fill: color,
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
