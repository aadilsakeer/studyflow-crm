import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
    Alert, Box, Button, Checkbox, Dialog, DialogContent, DialogTitle,
    FormControlLabel, MenuItem, Table, TableBody, TableCell, TableHead,
    TableRow, TextField, Typography,
} from "@mui/material";
import { getOwnerCompanies, getOwnerModuleCatalog, ownerOnboardTenant } from "../../services/owner";
import { showError } from "../../utils/toast";

const PLANS = ["starter", "growth", "enterprise", "custom"];

export default function OwnerCompaniesPage() {
    const navigate = useNavigate();
    const [rows, setRows] = useState([]);
    const [catalog, setCatalog] = useState([]);
    const [open, setOpen] = useState(false);
    const [credentials, setCredentials] = useState(null);
    const [form, setForm] = useState({
        name: "", email: "", admin_email: "", admin_first_name: "", admin_last_name: "",
        plan_code: "starter", module_codes: [],
    });

    const load = () => getOwnerCompanies().then((r) => setRows(r.data)).catch(() => showError("Load failed"));
    useEffect(() => {
        load();
        getOwnerModuleCatalog().then((r) => setCatalog(r.data.catalog || [])).catch(() => {});
    }, []);

    async function handleCreate() {
        try {
            const r = await ownerOnboardTenant(form);
            setOpen(false);
            setCredentials(r.data);
            load();
        } catch {
            showError("Onboarding failed");
        }
    }

    function toggleModule(code) {
        setForm((p) => ({
            ...p,
            module_codes: p.module_codes.includes(code)
                ? p.module_codes.filter((c) => c !== code)
                : [...p.module_codes, code],
        }));
    }

    return (
        <Box>
            <Box sx={{ display: "flex", justifyContent: "space-between", mb: 2 }}>
                <Typography variant="h4" fontWeight={700}>Companies</Typography>
                <Button variant="contained" onClick={() => setOpen(true)}>Onboard Tenant</Button>
            </Box>
            <Table size="small">
                <TableHead>
                    <TableRow>
                        <TableCell>Name</TableCell><TableCell>Plan</TableCell>
                        <TableCell>Status</TableCell><TableCell>Users</TableCell><TableCell>Active</TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {rows.map((r) => (
                        <TableRow key={r.id} hover sx={{ cursor: "pointer" }}
                            onClick={() => navigate(`/owner/companies/${r.id}`)}>
                            <TableCell>{r.name}</TableCell>
                            <TableCell>{r.plan || "—"}</TableCell>
                            <TableCell>{r.status || "—"}</TableCell>
                            <TableCell>{r.users}</TableCell>
                            <TableCell>{r.is_active ? "Yes" : "No"}</TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
            <Dialog open={open} onClose={() => setOpen(false)} fullWidth maxWidth="sm">
                <DialogTitle>Onboard Tenant</DialogTitle>
                <DialogContent>
                    {["name", "email", "admin_email", "admin_first_name", "admin_last_name"].map((f) => (
                        <TextField key={f} fullWidth label={f.replace(/_/g, " ")} sx={{ mt: 1 }}
                            value={form[f]} onChange={(e) => setForm((p) => ({ ...p, [f]: e.target.value }))} />
                    ))}
                    <TextField select fullWidth label="Plan" sx={{ mt: 1 }} value={form.plan_code}
                        onChange={(e) => setForm((p) => ({ ...p, plan_code: e.target.value }))}>
                        {PLANS.map((p) => <MenuItem key={p} value={p}>{p}</MenuItem>)}
                    </TextField>
                    <Typography variant="subtitle2" sx={{ mt: 2 }}>Modules</Typography>
                    {catalog.map(([code, name]) => (
                        <FormControlLabel key={code} control={
                            <Checkbox checked={form.module_codes.includes(code)}
                                onChange={() => toggleModule(code)} />
                        } label={name} />
                    ))}
                    <Button variant="contained" sx={{ mt: 2 }} onClick={handleCreate}>Create &amp; Generate Password</Button>
                </DialogContent>
            </Dialog>
            <Dialog open={!!credentials} onClose={() => setCredentials(null)} fullWidth>
                <DialogTitle>Tenant credentials — copy now</DialogTitle>
                <DialogContent>
                    <Alert severity="warning" sx={{ mb: 2 }}>Shown once. Store securely.</Alert>
                    <Typography component="div" sx={{ fontFamily: "monospace", lineHeight: 1.9 }}>
                        Company: {credentials?.company_name}<br />
                        Admin username: {credentials?.admin_username}<br />
                        Admin email: {credentials?.admin_email}<br />
                        Temporary password: {credentials?.temporary_password}<br />
                        Plan: {credentials?.plan_code || "default trial"}
                    </Typography>
                </DialogContent>
            </Dialog>
        </Box>
    );
}
