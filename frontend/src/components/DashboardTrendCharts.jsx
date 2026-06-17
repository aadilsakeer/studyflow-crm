import { Box } from "@mui/material";
import Grid from "@mui/material/Grid";

import DashboardChart from "./DashboardChart";

function formatRevenue(value) {
    const amount = Number(value) || 0;

    return new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency: "INR",
        maximumFractionDigits: 0,
    }).format(amount);
}

function DashboardTrendCharts({ trends, rangeLabel }) {
    const charts = [
        {
            title: "Lead Trend",
            subtitle: `New leads · ${rangeLabel}`,
            trend: trends?.leads || [],
            color: "#2563EB",
            seriesLabel: "Leads",
        },
        {
            title: "Student Conversion Trend",
            subtitle: `New students · ${rangeLabel}`,
            trend: trends?.students || [],
            color: "#10B981",
            seriesLabel: "Students",
        },
        {
            title: "Application Trend",
            subtitle: `New applications · ${rangeLabel}`,
            trend: trends?.applications || [],
            color: "#7C3AED",
            seriesLabel: "Applications",
        },
        {
            title: "Revenue Trend",
            subtitle: `Paid revenue · ${rangeLabel}`,
            trend: trends?.revenue || [],
            color: "#F59E0B",
            seriesLabel: "Revenue",
            valueFormatter: formatRevenue,
        },
    ];

    return (
        <Grid container spacing={3}>
            {charts.map((chart) => (
                <Grid
                    size={{ xs: 12, md: 6 }}
                    key={chart.title}
                >
                    <DashboardChart
                        {...chart}
                    />
                </Grid>
            ))}
        </Grid>
    );
}

export default DashboardTrendCharts;
