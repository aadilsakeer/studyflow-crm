import { useEffect, useState } from "react";
import {
    Box, Button, Checkbox, FormControlLabel, Paper, Table, TableBody,
    TableCell, TableHead, TableRow, Typography,
} from "@mui/material";
import LoadingState from "../../components/LoadingState";
import { getOwnerCompanies, getOwnerModuleCatalog, ownerBulkModuleAssign } from "../../services/owner";
import { showError, showSuccess } from "../../utils/toast";

export default function OwnerModulesPage() {
    const [catalog, setCatalog] = useState(null);
    const [companies, setCompanies] = useState([]);
    const [selectedCompanies, setSelectedCompanies] = useState([]);
    const [selectedModules, setSelectedModules] = useState([]);
    const [action, setAction] = useState("enable");

    useEffect(() => {
        Promise.all([getOwnerModuleCatalog(), getOwnerCompanies()])
            .then(([cat, cos]) => {
                setCatalog(cat.data);
                setCompanies(cos.data);
            })
            .catch(() => showError("Failed to load modules"));
    }, []);

    if (!catalog) return <LoadingState />;

    const toggle = (list, setList, id) => {
        setList(list.includes(id) ? list.filter((x) => x !== id) : [...list, id]);
    };

    async function bulkAssign() {
        if (!selectedCompanies.length || !selectedModules.length) {
            showError("Select companies and modules");
            return;
        }
        try {
            await ownerBulkModuleAssign({
                company_ids: selectedCompanies,
                module_codes: selectedModules,
                action,
                trial_days: 14,
            });
            showSuccess("Modules updated");
        } catch {
            showError("Bulk assign failed");
        }
    }

    return (
        <Box>
            <Typography variant="h4" fontWeight={700}>Module Licensing</Typography>
            <Typography color="text.secondary" sx={{ mb: 3 }}>
                Catalog, plan mappings, and bulk assignment
            </Typography>
            <Paper sx={{ p: 2, mb: 3, borderRadius: 3 }}>
                <Typography fontWeight={600} sx={{ mb: 1 }}>Module Catalog</Typography>
                <Table size="small">
                    <TableHead>
                        <TableRow>
                            <TableCell>Module</TableCell>
                            <TableCell>Code</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {catalog.catalog.map(([code, name]) => (
                            <TableRow key={code}>
                                <TableCell>{name}</TableCell>
                                <TableCell>{code}</TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </Paper>
            <Paper sx={{ p: 2, mb: 3, borderRadius: 3 }}>
                <Typography fontWeight={600} sx={{ mb: 1 }}>Plans</Typography>
                {catalog.plans.map((p) => (
                    <Typography key={p.code} variant="body2" sx={{ mb: 0.5 }}>
                        <strong>{p.name}</strong>: {p.modules.join(", ") || "Manual assignment"}
                    </Typography>
                ))}
            </Paper>
            <Paper sx={{ p: 2, borderRadius: 3 }}>
                <Typography fontWeight={600} sx={{ mb: 2 }}>Bulk Assignment</Typography>
                <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap", mb: 2 }}>
                    {["enable", "trial", "disable"].map((a) => (
                        <Button
                            key={a}
                            size="small"
                            variant={action === a ? "contained" : "outlined"}
                            onClick={() => setAction(a)}
                        >
                            {a}
                        </Button>
                    ))}
                </Box>
                <Typography variant="subtitle2">Companies</Typography>
                {companies.map((c) => (
                    <FormControlLabel
                        key={c.id}
                        control={
                            <Checkbox
                                checked={selectedCompanies.includes(c.id)}
                                onChange={() => toggle(selectedCompanies, setSelectedCompanies, c.id)}
                            />
                        }
                        label={c.name}
                    />
                ))}
                <Typography variant="subtitle2" sx={{ mt: 2 }}>Modules</Typography>
                {catalog.catalog.map(([code, name]) => (
                    <FormControlLabel
                        key={code}
                        control={
                            <Checkbox
                                checked={selectedModules.includes(code)}
                                onChange={() => toggle(selectedModules, setSelectedModules, code)}
                            />
                        }
                        label={name}
                    />
                ))}
                <Box sx={{ mt: 2 }}>
                    <Button variant="contained" onClick={bulkAssign}>Apply</Button>
                </Box>
            </Paper>
        </Box>
    );
}
