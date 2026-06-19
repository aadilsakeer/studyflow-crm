import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
    Box, Button, Dialog, DialogContent, DialogTitle,
    Table, TableBody, TableCell, TableHead, TableRow, TextField, Typography,
} from "@mui/material";
import { getOwnerCompanies, createOwnerCompany } from "../../services/owner";
import { showError, showSuccess } from "../../utils/toast";

export default function OwnerCompaniesPage() {
    const navigate = useNavigate();
    const [rows, setRows] = useState([]);
    const [open, setOpen] = useState(false);
    const [form, setForm] = useState({ name: "", email: "", admin_email: "", admin_password: "" });

    const load = () => getOwnerCompanies().then((r) => setRows(r.data)).catch(() => showError("Load failed"));
    useEffect(() => { load(); }, []);

    async function handleCreate() {
        try {
            await createOwnerCompany(form);
            showSuccess("Company created");
            setOpen(false);
            load();
        } catch {
            showError("Create failed");
        }
    }

    return (
        <Box>
            <Box sx={{ display: "flex", justifyContent: "space-between", mb: 2 }}>
                <Typography variant="h4" fontWeight={700}>Companies</Typography>
                <Button variant="contained" onClick={() => setOpen(true)}>Create Company</Button>
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
            <Dialog open={open} onClose={() => setOpen(false)} fullWidth>
                <DialogTitle>Create Company</DialogTitle>
                <DialogContent>
                    {["name", "email", "admin_email", "admin_password"].map((f) => (
                        <TextField key={f} fullWidth label={f} type={f.includes("password") ? "password" : "text"}
                            sx={{ mt: 1 }} value={form[f]}
                            onChange={(e) => setForm((p) => ({ ...p, [f]: e.target.value }))} />
                    ))}
                    <Button variant="contained" sx={{ mt: 2 }} onClick={handleCreate}>Create</Button>
                </DialogContent>
            </Dialog>
        </Box>
    );
}
