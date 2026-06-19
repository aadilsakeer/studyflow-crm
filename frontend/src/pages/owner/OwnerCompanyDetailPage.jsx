import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
    Box, Button, Paper, Tab, Tabs, Table, TableBody, TableCell,
    TableHead, TableRow, Typography,
} from "@mui/material";
import LoadingState from "../../components/LoadingState";
import {
    deleteOwnerCompany, getOwnerCompany, ownerCompanyAction, ownerImpersonate,
    ownerModuleAction, startImpersonation,
} from "../../services/owner";
import { showError, showSuccess } from "../../utils/toast";

export default function OwnerCompanyDetailPage() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [data, setData] = useState(null);
    const [tab, setTab] = useState(0);

    const load = () => getOwnerCompany(id).then((r) => setData(r.data)).catch(() => showError("Load failed"));
    useEffect(() => { load(); }, [id]);

    if (!data) return <LoadingState />;
    const c = data.company;

    async function act(payload, msg) {
        try { await ownerCompanyAction(id, payload); showSuccess(msg); load(); }
        catch { showError("Failed"); }
    }

    async function moduleAct(code, action) {
        try {
            await ownerModuleAction(id, { action, module_code: code });
            showSuccess(`${action} ${code}`);
            load();
        } catch { showError("Module action failed"); }
    }

    async function impersonate() {
        try {
            const r = await ownerImpersonate(id, data.admin_user_id);
            startImpersonation(r.data);
        } catch { showError("Impersonate failed"); }
    }

    const modules = data.modules || [];

    return (
        <Box>
            <Button size="small" onClick={() => navigate("/owner/companies")}>← Back</Button>
            <Typography variant="h4" fontWeight={700} sx={{ mt: 1 }}>{c.name}</Typography>
            <Typography color="text.secondary">{c.email} · Plan: {data.subscription?.plan}</Typography>
            <Box sx={{ mt: 2, display: "flex", gap: 1, flexWrap: "wrap" }}>
                <Button size="small" variant="contained" onClick={impersonate}>Login As Admin</Button>
                <Button size="small" onClick={() => act({ action: c.is_active ? "suspend" : "activate" }, "Updated")}>
                    {c.is_active ? "Suspend" : "Activate"}
                </Button>
                <Button size="small" onClick={() => act({ action: "extend_trial", days: 7 }, "Trial extended")}>+Trial</Button>
                <Button size="small" onClick={() => act({ action: "reset_usage" }, "Reset")}>Reset Usage</Button>
                <Button size="small" color="error" onClick={async () => {
                    await deleteOwnerCompany(id); navigate("/owner/companies");
                }}>Delete</Button>
            </Box>
            <Paper sx={{ mt: 3, p: 2, borderRadius: 3 }}>
                <Typography>Users: {data.counts.users} · Leads: {data.counts.leads} · Students: {data.counts.students}</Typography>
                <Typography>Documents: {data.counts.documents} · WhatsApp (month): {data.counts.whatsapp_month}</Typography>
            </Paper>
            <Paper sx={{ mt: 2, borderRadius: 3 }}>
                <Tabs value={tab} onChange={(_, v) => setTab(v)}>
                    <Tab label="Modules" /><Tab label="Billing" /><Tab label="Support" /><Tab label="Audit Logs" />
                </Tabs>
                {tab === 0 && (
                    <Table size="small">
                        <TableHead>
                            <TableRow>
                                <TableCell>Module</TableCell>
                                <TableCell>Status</TableCell>
                                <TableCell>Trial</TableCell>
                                <TableCell>Actions</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {modules.map((m) => (
                                <TableRow key={m.code}>
                                    <TableCell>{m.name}</TableCell>
                                    <TableCell>{m.is_accessible ? "Active" : "Inactive"}</TableCell>
                                    <TableCell>{m.is_trial ? "Yes" : "No"}</TableCell>
                                    <TableCell>
                                        <Button size="small" onClick={() => moduleAct(m.code, "enable")}>Enable</Button>
                                        <Button size="small" onClick={() => moduleAct(m.code, "trial")}>Trial</Button>
                                        <Button size="small" onClick={() => moduleAct(m.code, "disable")}>Disable</Button>
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                )}
                {tab === 1 && (
                    <Table size="small">
                        <TableBody>
                            {data.billing.map((b) => (
                                <TableRow key={b.invoice_number}>
                                    <TableCell>{b.invoice_number}</TableCell>
                                    <TableCell>₹{b.amount}</TableCell>
                                    <TableCell>{b.status}</TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                )}
                {tab === 2 && (
                    <Table size="small">
                        <TableBody>
                            {data.support.map((s) => (
                                <TableRow key={s.id}>
                                    <TableCell>{s.subject}</TableCell>
                                    <TableCell>{s.status}</TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                )}
                {tab === 3 && (
                    <Table size="small">
                        <TableBody>
                            {data.audit_logs.map((l) => (
                                <TableRow key={l.id}>
                                    <TableCell>{l.module}</TableCell>
                                    <TableCell>{l.action}</TableCell>
                                    <TableCell>{l.description}</TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                )}
            </Paper>
        </Box>
    );
}
