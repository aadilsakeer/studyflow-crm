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

function formatRevenue(value) {
    const amount = Number(value) || 0;

    return new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency: "INR",
        maximumFractionDigits: 0,
    }).format(amount);
}

function DashboardCards({ dashboard }) {
    const cards = [
        {
            title: "Total Leads",
            value: dashboard?.total_leads ?? 0,
            icon: <PeopleIcon />,
            color: "#2563EB",
        },
        {
            title: "Students",
            value: dashboard?.total_students ?? 0,
            icon: <SchoolIcon />,
            color: "#10B981",
        },
        {
            title: "Applications",
            value: dashboard?.total_applications ?? 0,
            icon: <DescriptionIcon />,
            color: "#7C3AED",
        },
        {
            title: "Revenue",
            value: formatRevenue(
                dashboard?.total_revenue
            ),
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
                        lg: 3,
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
                        </Box>
                    </Paper>
                </Grid>
            ))}
        </Grid>
    );
}

export default DashboardCards;
