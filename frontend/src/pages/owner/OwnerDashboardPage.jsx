import { useEffect, useState } from "react";
import { Box, Grid, Paper, Typography } from "@mui/material";
import LoadingState from "../../components/LoadingState";
import { getOwnerDashboard } from "../../services/owner";

function Stat({ label, value }) {
    return (
        <Paper sx={{ p: 2, borderRadius: 3 }}>
            <Typography variant="body2" color="text.secondary">{label}</Typography>
            <Typography variant="h5" fontWeight={700}>{value}</Typography>
        </Paper>
    );
}

export default function OwnerDashboardPage() {
    const [data, setData] = useState(null);

    useEffect(() => {
        getOwnerDashboard().then((r) => setData(r.data)).catch(() => {});
    }, []);

    if (!data) return <LoadingState />;
    const t = data.totals;

    return (
        <Box>
            <Typography variant="h4" fontWeight={700} sx={{ mb: 3 }}>Owner Dashboard</Typography>
            <Grid container spacing={2}>
                <Grid size={{ xs: 6, md: 3 }}><Stat label="Companies" value={t.companies} /></Grid>
                <Grid size={{ xs: 6, md: 3 }}><Stat label="Users" value={t.users} /></Grid>
                <Grid size={{ xs: 6, md: 3 }}><Stat label="Leads" value={t.leads} /></Grid>
                <Grid size={{ xs: 6, md: 3 }}><Stat label="Students" value={t.students} /></Grid>
                <Grid size={{ xs: 6, md: 3 }}><Stat label="MRR" value={`₹${t.mrr}`} /></Grid>
                <Grid size={{ xs: 6, md: 3 }}><Stat label="ARR" value={`₹${t.arr}`} /></Grid>
                <Grid size={{ xs: 6, md: 3 }}><Stat label="Revenue" value={`₹${t.revenue}`} /></Grid>
                <Grid size={{ xs: 6, md: 3 }}><Stat label="Open Tickets" value={t.open_tickets} /></Grid>
                <Grid size={12}>
                    <Paper sx={{ p: 2, borderRadius: 3 }}>
                        <Typography variant="subtitle2">System: {data.health?.status}</Typography>
                    </Paper>
                </Grid>
            </Grid>
        </Box>
    );
}
