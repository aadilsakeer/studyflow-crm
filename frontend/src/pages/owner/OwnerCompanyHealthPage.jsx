import { useEffect, useState } from "react";
import { Link as RouterLink, useNavigate, useParams } from "react-router-dom";
import {
    Box,
    Button,
    Chip,
    Grid,
    Paper,
    TextField,
    Typography,
} from "@mui/material";
import LoadingState from "../../components/LoadingState";
import { getOwnerCustomerSuccessCompany, updateOwnerCustomerSuccessCompany } from "../../services/owner";

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

function Stat({ label, value, sub }) {
    return (
        <Paper sx={{ p: 2, borderRadius: 3, height: "100%" }}>
            <Typography variant="body2" color="text.secondary">{label}</Typography>
            <Typography variant="h5" fontWeight={700}>{value}</Typography>
            {sub && <Typography variant="caption" color="text.secondary">{sub}</Typography>}
        </Paper>
    );
}

export default function OwnerCompanyHealthPage() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [data, setData] = useState(null);
    const [notes, setNotes] = useState("");
    const [renewalDate, setRenewalDate] = useState("");
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        getOwnerCustomerSuccessCompany(id)
            .then((r) => {
                setData(r.data);
                setNotes(r.data.meeting_notes || "");
                setRenewalDate(r.data.renewal_date || "");
            })
            .catch(() => setData(null));
    }, [id]);

    const save = () => {
        setSaving(true);
        updateOwnerCustomerSuccessCompany(id, {
            meeting_notes: notes,
            renewal_date: renewalDate || null,
        })
            .then((r) => setData(r.data))
            .finally(() => setSaving(false));
    };

    if (!data) return <LoadingState />;

    const login = data.login_activity || {};
    const adoption = data.feature_adoption || {};
    const tickets = data.ticket_volume || {};

    return (
        <Box>
            <Button component={RouterLink} to="/owner/customer-success" sx={{ mb: 2 }}>
                ← Back to Customer Success
            </Button>
            <Box sx={{ display: "flex", alignItems: "center", gap: 2, mb: 3, flexWrap: "wrap" }}>
                <Typography variant="h4" fontWeight={700}>{data.company_name}</Typography>
                <Chip label={`Health ${data.health_score}`} sx={{ bgcolor: healthColor(data.health_score), color: "#fff" }} />
                <Chip label={`Renewal ${data.renewal_risk}`} color={riskColor(data.renewal_risk)} />
            </Box>

            <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid size={{ xs: 6, md: 3 }}>
                    <Stat label="Health score" value={data.health_score} />
                </Grid>
                <Grid size={{ xs: 6, md: 3 }}>
                    <Stat label="Login rate (30d)" value={`${login.login_rate ?? 0}%`} sub={`${login.active_users_30d ?? 0}/${login.total_users ?? 0} users`} />
                </Grid>
                <Grid size={{ xs: 6, md: 3 }}>
                    <Stat label="Modules active" value={adoption.modules_active ?? 0} sub={`${adoption.modules_enabled ?? 0} enabled`} />
                </Grid>
                <Grid size={{ xs: 6, md: 3 }}>
                    <Stat label="Open tickets" value={tickets.open ?? 0} sub={`${tickets.month ?? 0} this month`} />
                </Grid>
            </Grid>

            <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid size={{ xs: 12, md: 6 }}>
                    <Paper sx={{ p: 2, borderRadius: 3 }}>
                        <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>Success manager</Typography>
                        {data.success_manager ? (
                            <Typography>{data.success_manager.name} — {data.success_manager.email}</Typography>
                        ) : (
                            <Typography color="text.secondary">Unassigned</Typography>
                        )}
                        <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                            Plan: {data.subscription?.plan ?? "—"} · Status: {data.subscription?.status ?? "—"}
                        </Typography>
                        <Button sx={{ mt: 2 }} size="small" onClick={() => navigate(`/owner/companies/${id}`)}>
                            Open company console
                        </Button>
                    </Paper>
                </Grid>
                <Grid size={{ xs: 12, md: 6 }}>
                    <Paper sx={{ p: 2, borderRadius: 3 }}>
                        <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>Renewal tracking</Typography>
                        <TextField
                            fullWidth
                            type="date"
                            label="Renewal date"
                            value={renewalDate}
                            onChange={(e) => setRenewalDate(e.target.value)}
                            InputLabelProps={{ shrink: true }}
                            sx={{ mb: 2 }}
                        />
                        <TextField
                            fullWidth
                            multiline
                            minRows={3}
                            label="Meeting notes"
                            value={notes}
                            onChange={(e) => setNotes(e.target.value)}
                            sx={{ mb: 2 }}
                        />
                        <Button variant="contained" onClick={save} disabled={saving}>
                            {saving ? "Saving…" : "Save"}
                        </Button>
                    </Paper>
                </Grid>
            </Grid>

            <Paper sx={{ p: 2, borderRadius: 3 }}>
                <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>Customer timeline</Typography>
                {(data.timeline || []).length === 0 && (
                    <Typography color="text.secondary">No events yet.</Typography>
                )}
                {(data.timeline || []).map((ev, i) => (
                    <Box key={i} sx={{ py: 1.5, borderBottom: "1px solid #e2e8f0" }}>
                        <Box sx={{ display: "flex", justifyContent: "space-between", gap: 2 }}>
                            <Typography fontWeight={600}>{ev.title}</Typography>
                            <Chip size="small" label={ev.source || ev.type} variant="outlined" />
                        </Box>
                        <Typography variant="body2" color="text.secondary">{ev.body}</Typography>
                        {ev.created_at && (
                            <Typography variant="caption" color="text.secondary">
                                {new Date(ev.created_at).toLocaleString()}
                            </Typography>
                        )}
                    </Box>
                ))}
            </Paper>
        </Box>
    );
}
