import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
    Box,
    Chip,
    Grid,
    Paper,
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableRow,
    Typography,
} from "@mui/material";
import LoadingState from "../../components/LoadingState";
import { getOwnerCustomerSuccessAlerts, getOwnerCustomerSuccessDashboard } from "../../services/owner";

function Stat({ label, value }) {
    return (
        <Paper sx={{ p: 2, borderRadius: 3 }}>
            <Typography variant="body2" color="text.secondary">{label}</Typography>
            <Typography variant="h5" fontWeight={700}>{value}</Typography>
        </Paper>
    );
}

function riskColor(risk) {
    if (risk === "high") return "error";
    if (risk === "medium") return "warning";
    return "success";
}

function healthColor(score) {
    if (score < 40) return "#ef4444";
    if (score < 65) return "#f59e0b";
    return "#22c55e";
}

export default function OwnerCustomerSuccessPage() {
    const [data, setData] = useState(null);
    const [alerts, setAlerts] = useState([]);
    const navigate = useNavigate();

    useEffect(() => {
        Promise.all([
            getOwnerCustomerSuccessDashboard(),
            getOwnerCustomerSuccessAlerts(),
        ])
            .then(([dash, alertRes]) => {
                setData(dash.data);
                setAlerts(alertRes.data.alerts || []);
            })
            .catch(() => setData(null));
    }, []);

    if (!data) return <LoadingState />;
    const t = data.totals || {};

    return (
        <Box>
            <Typography variant="h4" fontWeight={700} sx={{ mb: 1 }}>Customer Success</Typography>
            <Typography color="text.secondary" sx={{ mb: 3 }}>
                Health scores, renewal risk, feature adoption, and account timelines across tenants.
            </Typography>

            <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid size={{ xs: 6, md: 3 }}><Stat label="Active companies" value={t.companies ?? 0} /></Grid>
                <Grid size={{ xs: 6, md: 3 }}><Stat label="At-risk accounts" value={t.at_risk ?? 0} /></Grid>
                <Grid size={{ xs: 6, md: 3 }}><Stat label="Avg health score" value={t.avg_health ?? 0} /></Grid>
                <Grid size={{ xs: 6, md: 3 }}><Stat label="Renewal alerts" value={t.open_alerts ?? alerts.length} /></Grid>
            </Grid>

            <Paper sx={{ p: 2, mb: 3, borderRadius: 3 }}>
                <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>Renewal alerts</Typography>
                {alerts.length === 0 && (
                    <Typography color="text.secondary">No accounts at elevated renewal risk.</Typography>
                )}
                {alerts.map((a) => (
                    <Paper
                        key={a.company_id}
                        sx={{
                            p: 1.5,
                            mb: 1,
                            borderRadius: 2,
                            cursor: "pointer",
                            borderLeft: 4,
                            borderColor: a.renewal_risk === "high" ? "#ef4444" : "#f59e0b",
                        }}
                        onClick={() => navigate(`/owner/customer-success/companies/${a.company_id}`)}
                    >
                        <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 2 }}>
                            <Box>
                                <Typography fontWeight={600}>{a.company_name}</Typography>
                                <Typography variant="body2" color="text.secondary">{a.reason}</Typography>
                            </Box>
                            <Box sx={{ display: "flex", gap: 1, alignItems: "center" }}>
                                <Chip size="small" label={`Health ${a.health_score}`} sx={{ bgcolor: healthColor(a.health_score), color: "#fff" }} />
                                <Chip size="small" label={a.renewal_risk} color={riskColor(a.renewal_risk)} />
                            </Box>
                        </Box>
                    </Paper>
                ))}
            </Paper>

            <Paper sx={{ borderRadius: 3, overflow: "hidden" }}>
                <Typography variant="h6" fontWeight={600} sx={{ p: 2, pb: 0 }}>Company health</Typography>
                <Table size="small">
                    <TableHead>
                        <TableRow>
                            <TableCell>Company</TableCell>
                            <TableCell align="right">Health</TableCell>
                            <TableCell align="right">Renewal risk</TableCell>
                            <TableCell align="right">Login rate</TableCell>
                            <TableCell align="right">Open tickets</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {(data.companies || []).map((c) => (
                            <TableRow
                                key={c.company_id}
                                hover
                                sx={{ cursor: "pointer" }}
                                onClick={() => navigate(`/owner/customer-success/companies/${c.company_id}`)}
                            >
                                <TableCell>{c.company_name}</TableCell>
                                <TableCell align="right">{c.health_score}</TableCell>
                                <TableCell align="right">
                                    <Chip size="small" label={c.renewal_risk} color={riskColor(c.renewal_risk)} />
                                </TableCell>
                                <TableCell align="right">{c.login_activity?.login_rate ?? 0}%</TableCell>
                                <TableCell align="right">{c.ticket_volume?.open ?? 0}</TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </Paper>
        </Box>
    );
}
