import { useState } from "react";
import LeadDrawer from "../components/LeadDrawer";
import useLeads from "../hooks/useLeads";
import usePermissions from "../hooks/usePermissions";
import LeadDialog from "../components/LeadDialog";
import LoadingState from "../components/LoadingState";
import {
    Paper,
    Typography,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Chip,
    Button,
    Box,
    TextField,
    MenuItem,
    TablePagination,
} from "@mui/material";

const STATUS_OPTIONS = [
    { value: "", label: "All Statuses" },
    { value: "new", label: "New" },
    { value: "contacted", label: "Contacted" },
    { value: "interested", label: "Interested" },
    { value: "follow_up", label: "Follow Up" },
    { value: "converted", label: "Converted" },
    { value: "lost", label: "Lost" },
];

function LeadsPage() {
    const [search, setSearch] = useState("");
    const [status, setStatus] = useState("");
    const [page, setPage] = useState(0);
    const [open, setOpen] = useState(false);
    const [selectedLead, setSelectedLead] =
        useState(null);
    const [drawerOpen, setDrawerOpen] =
        useState(false);

    const { can } = usePermissions();

    const { leads, count, loading, reload } =
        useLeads({
            search,
            status,
            page: page + 1,
        });

    function handleLeadUpdated(updatedLead) {
        setSelectedLead(updatedLead);
        reload();
    }

    function handleLeadDeleted() {
        setSelectedLead(null);
        setDrawerOpen(false);
        reload();
    }

    if (loading && leads.length === 0) {
        return (
            <LoadingState message="Loading leads..." />
        );
    }

    return (
        <>
            <LeadDialog
                open={open}
                onClose={() => setOpen(false)}
                onSuccess={reload}
            />
            <LeadDrawer
                open={drawerOpen}
                onClose={() =>
                    setDrawerOpen(false)
                }
                lead={selectedLead}
                onLeadUpdated={
                    handleLeadUpdated
                }
                onLeadDeleted={
                    handleLeadDeleted
                }
            />

            <Paper
                elevation={0}
                sx={{
                    p: 3,
                    borderRadius: 4,
                    border:
                        "1px solid #E5E7EB",
                }}
            >
                <Box
                    sx={{
                        display: "flex",
                        justifyContent:
                            "space-between",
                        alignItems:
                            "center",
                        mb: 3,
                        flexWrap: "wrap",
                        gap: 2,
                    }}
                >
                    <Typography
                        variant="h5"
                        fontWeight={700}
                    >
                        Leads Management
                    </Typography>

                    {can("leads.add") && (
                        <Button
                            variant="contained"
                            onClick={() =>
                                setOpen(true)
                            }
                        >
                            Add Lead
                        </Button>
                    )}
                </Box>

                <Box
                    sx={{
                        display: "flex",
                        gap: 2,
                        mb: 3,
                        flexWrap: "wrap",
                    }}
                >
                    <TextField
                        size="small"
                        placeholder="Search name, phone, email..."
                        value={search}
                        onChange={(e) => {
                            setSearch(
                                e.target.value
                            );
                            setPage(0);
                        }}
                        sx={{ minWidth: 260 }}
                    />

                    <TextField
                        select
                        size="small"
                        label="Status"
                        value={status}
                        onChange={(e) => {
                            setStatus(
                                e.target.value
                            );
                            setPage(0);
                        }}
                        sx={{ minWidth: 180 }}
                    >
                        {STATUS_OPTIONS.map(
                            (opt) => (
                                <MenuItem
                                    key={
                                        opt.value
                                    }
                                    value={
                                        opt.value
                                    }
                                >
                                    {opt.label}
                                </MenuItem>
                            )
                        )}
                    </TextField>
                </Box>

                <TableContainer>
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell>
                                    Name
                                </TableCell>
                                <TableCell>
                                    Phone
                                </TableCell>
                                <TableCell>
                                    Email
                                </TableCell>
                                <TableCell>
                                    Country
                                </TableCell>
                                <TableCell>
                                    Status
                                </TableCell>
                            </TableRow>
                        </TableHead>

                        <TableBody>
                            {leads.length ===
                            0 ? (
                                <TableRow>
                                    <TableCell
                                        colSpan={
                                            5
                                        }
                                        align="center"
                                    >
                                        No leads
                                        found
                                    </TableCell>
                                </TableRow>
                            ) : (
                                leads.map(
                                    (lead) => (
                                        <TableRow
                                            key={
                                                lead.id
                                            }
                                            hover
                                            onClick={() => {
                                                setSelectedLead(
                                                    lead
                                                );
                                                setDrawerOpen(
                                                    true
                                                );
                                            }}
                                            sx={{
                                                cursor:
                                                    "pointer",
                                            }}
                                        >
                                            <TableCell>
                                                {
                                                    lead.first_name
                                                }{" "}
                                                {
                                                    lead.last_name
                                                }
                                            </TableCell>
                                            <TableCell>
                                                {
                                                    lead.phone
                                                }
                                            </TableCell>
                                            <TableCell>
                                                {
                                                    lead.email
                                                }
                                            </TableCell>
                                            <TableCell>
                                                {
                                                    lead.country_interest
                                                }
                                            </TableCell>
                                            <TableCell>
                                                <Chip
                                                    label={
                                                        lead.status
                                                    }
                                                    color="success"
                                                    size="small"
                                                />
                                            </TableCell>
                                        </TableRow>
                                    )
                                )
                            )}
                        </TableBody>
                    </Table>
                </TableContainer>

                <TablePagination
                    component="div"
                    count={count}
                    page={page}
                    onPageChange={(
                        _e,
                        newPage
                    ) =>
                        setPage(newPage)
                    }
                    rowsPerPage={20}
                    rowsPerPageOptions={[
                        20,
                    ]}
                />
            </Paper>
        </>
    );
}

export default LeadsPage;
