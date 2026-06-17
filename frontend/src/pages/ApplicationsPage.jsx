import { useState } from "react";

import useApplications from "../hooks/useApplications";
import ApplicationDrawer from "../components/ApplicationDrawer";
import ApplicationDialog from "../components/ApplicationDialog";
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
} from "@mui/material";

const STATUS_OPTIONS = [
    { value: "", label: "All Statuses" },
    { value: "draft", label: "Draft" },
    {
        value: "submitted",
        label: "Submitted",
    },
    {
        value: "offer_received",
        label: "Offer Received",
    },
    {
        value: "rejected",
        label: "Rejected",
    },
    {
        value: "visa_processing",
        label: "Visa Processing",
    },
    {
        value: "completed",
        label: "Completed",
    },
];

function ApplicationsPage() {
    const [search, setSearch] =
        useState("");
    const [status, setStatus] =
        useState("");
    const [dialogOpen, setDialogOpen] =
        useState(false);
    const [selected, setSelected] =
        useState(null);
    const [drawerOpen, setDrawerOpen] =
        useState(false);

    const {
        applications,
        loading,
        reload,
    } = useApplications({
        search,
        status,
    });

    if (loading && applications.length === 0) {
        return (
            <LoadingState message="Loading applications..." />
        );
    }

    return (
        <>
            <ApplicationDialog
                open={dialogOpen}
                onClose={() =>
                    setDialogOpen(false)
                }
                onSuccess={reload}
            />

            <ApplicationDrawer
                open={drawerOpen}
                onClose={() =>
                    setDrawerOpen(false)
                }
                application={selected}
                onUpdated={reload}
                onDeleted={reload}
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
                        Applications
                    </Typography>

                    <Button
                        variant="contained"
                        onClick={() =>
                            setDialogOpen(true)
                        }
                    >
                        New Application
                    </Button>
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
                        placeholder="Search student, university, course..."
                        value={search}
                        onChange={(e) =>
                            setSearch(
                                e.target.value
                            )
                        }
                        sx={{ minWidth: 280 }}
                    />

                    <TextField
                        select
                        size="small"
                        label="Status"
                        value={status}
                        onChange={(e) =>
                            setStatus(
                                e.target.value
                            )
                        }
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
                                    Student
                                </TableCell>
                                <TableCell>
                                    University
                                </TableCell>
                                <TableCell>
                                    Course
                                </TableCell>
                                <TableCell>
                                    Intake
                                </TableCell>
                                <TableCell>
                                    Status
                                </TableCell>
                            </TableRow>
                        </TableHead>

                        <TableBody>
                            {applications.length
                            === 0 ? (
                                <TableRow>
                                    <TableCell
                                        colSpan={
                                            5
                                        }
                                        align="center"
                                    >
                                        No
                                        applications
                                        found
                                    </TableCell>
                                </TableRow>
                            ) : (
                                applications.map(
                                    (app) => (
                                        <TableRow
                                            key={
                                                app.id
                                            }
                                            hover
                                            onClick={() => {
                                                setSelected(
                                                    app
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
                                                    app.student_name
                                                }
                                                <Typography
                                                    variant="caption"
                                                    display="block"
                                                    color="text.secondary"
                                                >
                                                    {
                                                        app.student_code
                                                    }
                                                </Typography>
                                            </TableCell>
                                            <TableCell>
                                                {
                                                    app.university_name
                                                }
                                            </TableCell>
                                            <TableCell>
                                                {
                                                    app.course_name
                                                }
                                            </TableCell>
                                            <TableCell>
                                                {
                                                    app.intake
                                                }
                                            </TableCell>
                                            <TableCell>
                                                <Chip
                                                    label={
                                                        app.application_status
                                                    }
                                                    size="small"
                                                    color="primary"
                                                />
                                            </TableCell>
                                        </TableRow>
                                    )
                                )
                            )}
                        </TableBody>
                    </Table>
                </TableContainer>
            </Paper>
        </>
    );
}

export default ApplicationsPage;
