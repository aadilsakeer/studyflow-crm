import {
    Paper,
    Typography,
    Box,
} from "@mui/material";

import Grid from "@mui/material/Grid";

import PeopleIcon from "@mui/icons-material/People";
import SchoolIcon from "@mui/icons-material/School";
import DescriptionIcon from "@mui/icons-material/Description";
import CurrencyRupeeIcon from "@mui/icons-material/CurrencyRupee";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import VerifiedIcon from "@mui/icons-material/Verified";

function formatRevenue(value) {
    const amount = Number(value) || 0;

    return new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency: "INR",
        maximumFractionDigits: 0,
    }).format(amount);
}

function GrowthBadge({ growth }) {
    const value = Number(growth) || 0;
    const color = value > 0
        ? "#10B981"
        : value < 0
            ? "#EF4444"
            : "#64748B";
    const prefix = value > 0 ? "+" : "";

    return (
        <Typography
            variant="caption"
            sx={{ color, fontWeight: 600 }}
        >
            {prefix}
            {value}% vs prev period
        </Typography>
    );
}

function DashboardCards({ dashboard }) {
    const kpis = dashboard?.kpis || {};

    const cards = [
        {
            title: "Total Leads",
            value: kpis.total_leads?.value ?? 0,
            growth: kpis.total_leads?.growth_pct,
            icon: <PeopleIcon />,
            color: "#2563EB",
        },
        {
            title: "Qualified Leads",
            value: kpis.qualified_leads?.value ?? 0,
            growth: kpis.qualified_leads?.growth_pct,
            icon: <VerifiedIcon />,
            color: "#0EA5E9",
        },
        {
            title: "Students",
            value: kpis.students?.value ?? 0,
            growth: kpis.students?.growth_pct,
            icon: <SchoolIcon />,
            color: "#10B981",
        },
        {
            title: "Applications",
            value: kpis.applications?.value ?? 0,
            growth: kpis.applications?.growth_pct,
            icon: <DescriptionIcon />,
            color: "#7C3AED",
        },
        {
            title: "Conversion Rate",
            value: `${kpis.conversion_rate?.value ?? 0}%`,
            growth: kpis.conversion_rate?.growth_pct,
            icon: <TrendingUpIcon />,
            color: "#6366F1",
        },
        {
            title: "Revenue",
            value: formatRevenue(
                kpis.revenue?.value,
            ),
            growth: kpis.revenue?.growth_pct,
            icon: <CurrencyRupeeIcon />,
            color: "#F59E0B",
        },
    ];

    return (
        <Grid container spacing={3}>
            {cards.map((card) => (
                <Grid
                    size={{
                        xs: 12,
                        sm: 6,
                        lg: 4,
                    }}
                    key={card.title}
                >
                    <Paper
                        elevation={0}
                        sx={{
                            p: 3,
                            borderRadius: 4,
                            border: "1px solid #E5E7EB",
                            backgroundColor: "#FFFFFF",
                            height: "100%",
                        }}
                    >
                        <Box
                            sx={{
                                display: "flex",
                                justifyContent: "space-between",
                                alignItems: "center",
                            }}
                        >
                            <Typography
                                variant="body2"
                                color="text.secondary"
                            >
                                {card.title}
                            </Typography>

                            <Box sx={{ color: card.color }}>
                                {card.icon}
                            </Box>
                        </Box>

                        <Box mt={2}>
                            <Typography
                                variant="h5"
                                fontWeight={700}
                            >
                                {card.value}
                            </Typography>

                            <Box mt={1}>
                                <GrowthBadge
                                    growth={card.growth}
                                />
                            </Box>
                        </Box>
                    </Paper>
                </Grid>
            ))}
        </Grid>
    );
}

export default DashboardCards;
