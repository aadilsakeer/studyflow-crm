import { useCallback, useEffect, useState } from "react";
import {
    Box, Button, Chip, Grid, Paper, Tab, Tabs,
    Table, TableBody, TableCell, TableHead, TableRow, Typography,
} from "@mui/material";
import LoadingState from "../components/LoadingState";
import usePermissions from "../hooks/usePermissions";
import {
    adminExtendTrial, adminImpersonate, adminResetUsage,
    adminTenantAction, adminTicketOps, getAdminDashboard,
    getAdminOperations, getAdminSupportTickets, getProductionOps, postProductionOps,
} from "../services/saas";
import { showError, showSuccess } from "../utils/toast";

function StatCard({ label, value }) {
    return (
        <Paper sx={{ p: 2.5, borderRadius: 4 }}>
            <Typography color="text.secondary" variant="body2">{label}</Typography>
            <Typography variant="h4" fontWeight={700}>{value}</Typography>
        </Paper>
    );
}

export default function SaasAdminPage() {
    const { user } = usePermissions();
    const [tab, setTab] = useState(0);
    const [loading, setLoading] = useState(true);
    const [dashboard, setDashboard] = useState(null);
    const [ops, setOps] = useState(null);
    const [tickets, setTickets] = useState([]);

    const [prod, setProd] = useState(null);

    const load = useCallback(() => {
        if (!user?.is_superuser) return;
        Promise.all([getAdminDashboard(), getAdminOperations(), getAdminSupportTickets(), getProductionOps()])
            .then(([d, o, t, p]) => { setDashboard(d.data); setOps(o.data); setTickets(t.data); setProd(p.data); })
            .catch(() => showError("Failed to load"))
            .finally(() => setLoading(false));
    }, [user]);

    useEffect(() => { load(); }, [load]);

    if (!user?.is_superuser) return <Typography>Superuser required.</Typography>;
    if (loading) return <LoadingState />;

    const t = ops?.totals || dashboard?.totals || {};

    async function act(promise, msg) {
        try { await promise; showSuccess(msg); load(); } catch { showError("Action failed"); }
    }

    return (
        <Box>
            <Typography variant="h4" fontWeight={700} sx={{ mb: 3 }}>Platform Operations</Typography>
            <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid size={{ xs: 6, md: 2 }}><StatCard label="Tenants" value={t.companies || 0} /></Grid>
                <Grid size={{ xs: 6, md: 2 }}><StatCard label="Active" value={t.active_subscriptions || 0} /></Grid>
                <Grid size={{ xs: 6, md: 2 }}><StatCard label="Trials" value={t.trials || 0} /></Grid>
                <Grid size={{ xs: 6, md: 2 }}><StatCard label="Monthly Rev" value={`₹${t.monthly_revenue || 0}`} /></Grid>
                <Grid size={{ xs: 6, md: 2 }}><StatCard label="Open Tickets" value={t.open_support_tickets || 0} /></Grid>
            </Grid>
            <Paper sx={{ p: 2, borderRadius: 4 }}>
                <Tabs value={tab} onChange={(_, v) => setTab(v)}>
                    <Tab label="Tenants" /><Tab label="Subscriptions" /><Tab label="Support" /><Tab label="Production" />
                </Tabs>
                {tab === 0 && (
                    <Table size="small" sx={{ mt: 2 }}>
                        <TableHead><TableRow>
                            <TableCell>Company</TableCell><TableCell>Status</TableCell><TableCell>Plan</TableCell><TableCell>Actions</TableCell>
                        </TableRow></TableHead>
                        <TableBody>
                            {(dashboard?.companies || []).map((r) => (
                                <TableRow key={r.id}>
                                    <TableCell>{r.name}</TableCell>
                                    <TableCell>{r.is_active ? "Active" : "Suspended"}</TableCell>
                                    <TableCell>{r.plan || "—"}</TableCell>
                                    <TableCell>
                                        <Button size="small" onClick={() => act(adminTenantAction(r.id, r.is_active ? "suspend" : "activate"), "Updated")}>
                                            {r.is_active ? "Suspend" : "Activate"}
                                        </Button>
                                        <Button size="small" onClick={() => act(adminExtendTrial(r.id), "Trial extended")}>+Trial</Button>
                                        <Button size="small" onClick={() => act(adminResetUsage(r.id), "Usage reset")}>Reset</Button>
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                )}
                {tab === 1 && (
                    <Box sx={{ mt: 2 }}>
                        <Typography variant="subtitle2">Failed Payments</Typography>
                        {(ops?.failed_payments || []).map((p) => (
                            <Typography key={p.id} variant="body2">Co#{p.company_id} ₹{p.amount} ({p.provider})</Typography>
                        ))}
                        <Typography variant="subtitle2" sx={{ mt: 2 }}>Expiring</Typography>
                        {(ops?.expiring_subscriptions || []).map((e, i) => (
                            <Typography key={i} variant="body2">{e.company__name} — {e.plan__name}</Typography>
                        ))}
                        <Typography variant="subtitle2" sx={{ mt: 2 }}>Renewals (month)</Typography>
                        {(ops?.renewals || []).map((r) => (
                            <Typography key={r.invoice_number} variant="body2">{r.invoice_number} ₹{r.amount}</Typography>
                        ))}
                    </Box>
                )}
                {tab === 2 && (
                    <Table size="small" sx={{ mt: 2 }}>
                        <TableHead><TableRow>
                            <TableCell>Tenant</TableCell><TableCell>Subject</TableCell><TableCell>SLA</TableCell><TableCell>Actions</TableCell>
                        </TableRow></TableHead>
                        <TableBody>
                            {tickets.map((tk) => (
                                <TableRow key={tk.id}>
                                    <TableCell>{tk.company_name}</TableCell>
                                    <TableCell>{tk.subject}</TableCell>
                                    <TableCell><Chip size="small" label={tk.sla_status} color={tk.sla_status === "breached" ? "error" : "default"} /></TableCell>
                                    <TableCell>
                                        <Button size="small" onClick={() => act(adminTicketOps(tk.id, { escalate: true }), "Escalated")}>Escalate</Button>
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                )}
                {tab === 3 && prod && (
                    <Box sx={{ mt: 2 }}>
                        <Chip label={prod.status} color={prod.status === "healthy" ? "success" : "warning"} sx={{ mb: 2 }} />
                        {(prod.alerts || []).map((a) => <Chip key={a} label={a} color="error" size="small" sx={{ mr: 1 }} />)}
                        <Typography variant="body2">DB: {prod.database?.ok ? "OK" : "FAIL"}</Typography>
                        <Typography variant="body2">Stripe: {prod.payments?.stripe?.ok ? "OK" : "—"}</Typography>
                        <Typography variant="body2">Razorpay: {prod.payments?.razorpay?.ok ? "OK" : "—"}</Typography>
                        <Typography variant="body2">Celery workers: {(prod.celery?.workers || []).join(", ") || "none"}</Typography>
                        <Typography variant="body2">Backup: {prod.backup?.file || "none"}</Typography>
                        <Typography variant="body2" color={prod.pg_dump?.ok ? "text.primary" : "error.main"}>
                            pg_dump: {prod.pg_dump?.ok ? prod.pg_dump.path : (prod.pg_dump?.error || "unknown")}
                        </Typography>
                        <Box sx={{ mt: 2, display: "flex", gap: 1 }}>
                            <Button size="small" variant="outlined" onClick={() => act(postProductionOps({ action: "validate_payments" }), "Validated")}>Validate Payments</Button>
                            <Button size="small" variant="outlined" onClick={() => act(postProductionOps({ action: "verify_email", email: user.email }), "Email sent")}>Test Email</Button>
                        </Box>
                    </Box>
                )}
            </Paper>
        </Box>
    );
}
