import { useEffect, useState } from "react";

import {
    Paper,
    Typography,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Button,
    Box,
    TextField,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Chip,
} from "@mui/material";

import {
    getUniversities,
    createUniversity,
} from "../services/universities";

import { formatApiError } from "../services/leads";
import {
    showError,
    showSuccess,
} from "../utils/toast";

import LoadingState from "../components/LoadingState";
import usePermissions from "../hooks/usePermissions";

function UniversitiesPage() {
    const { can } = usePermissions();
    const [universities, setUniversities] =
        useState([]);
    const [loading, setLoading] =
        useState(true);
    const [search, setSearch] =
        useState("");
    const [open, setOpen] =
        useState(false);
    const [form, setForm] = useState({
        name: "",
        country: "",
        city: "",
        website: "",
    });

    useEffect(() => {
        loadUniversities();
    }, [search]);

    async function loadUniversities() {
        setLoading(true);

        try {
            const params = search
                ? { search }
                : {};
            const data =
                await getUniversities(params);
            setUniversities(
                Array.isArray(data)
                    ? data
                    : data.results || []
            );
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    }

    async function handleSave() {
        if (!form.name.trim()) {
            showError("Name is required");
            return;
        }

        if (!form.country.trim()) {
            showError("Country is required");
            return;
        }

        try {
            await createUniversity(form);
            setForm({
                name: "",
                country: "",
                city: "",
                website: "",
            });
            setOpen(false);
            loadUniversities();
            showSuccess("University added");
        } catch (error) {
            showError(formatApiError(error));
        }
    }

    if (loading && universities.length === 0) {
        return (
            <LoadingState message="Loading universities..." />
        );
    }

    return (
        <>
            <Dialog
                open={open}
                onClose={() => setOpen(false)}
                maxWidth="sm"
                fullWidth
            >
                <DialogTitle>
                    Add University
                </DialogTitle>

                <DialogContent>
                    <TextField
                        label="Name"
                        required
                        fullWidth
                        margin="normal"
                        value={form.name}
                        onChange={(e) =>
                            setForm({
                                ...form,
                                name:
                                    e.target
                                        .value,
                            })
                        }
                    />
                    <TextField
                        label="Country"
                        required
                        fullWidth
                        margin="normal"
                        value={form.country}
                        onChange={(e) =>
                            setForm({
                                ...form,
                                country:
                                    e.target
                                        .value,
                            })
                        }
                    />
                    <TextField
                        label="City"
                        fullWidth
                        margin="normal"
                        value={form.city}
                        onChange={(e) =>
                            setForm({
                                ...form,
                                city:
                                    e.target
                                        .value,
                            })
                        }
                    />
                    <TextField
                        label="Website"
                        fullWidth
                        margin="normal"
                        value={form.website}
                        onChange={(e) =>
                            setForm({
                                ...form,
                                website:
                                    e.target
                                        .value,
                            })
                        }
                    />
                </DialogContent>

                <DialogActions>
                    <Button
                        onClick={() =>
                            setOpen(false)
                        }
                    >
                        Cancel
                    </Button>
                    <Button
                        variant="contained"
                        onClick={handleSave}
                    >
                        Save
                    </Button>
                </DialogActions>
            </Dialog>

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
                        Universities
                    </Typography>

                    {can("universities.add") && (
                        <Button
                            variant="contained"
                            onClick={() =>
                                setOpen(true)
                            }
                        >
                            Add University
                        </Button>
                    )}
                </Box>

                <TextField
                    size="small"
                    placeholder="Search universities..."
                    value={search}
                    onChange={(e) =>
                        setSearch(
                            e.target.value
                        )
                    }
                    sx={{
                        mb: 3,
                        minWidth: 280,
                    }}
                />

                <TableContainer>
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell>
                                    Name
                                </TableCell>
                                <TableCell>
                                    Country
                                </TableCell>
                                <TableCell>
                                    City
                                </TableCell>
                                <TableCell>
                                    Status
                                </TableCell>
                            </TableRow>
                        </TableHead>

                        <TableBody>
                            {universities.length
                            === 0 ? (
                                <TableRow>
                                    <TableCell
                                        colSpan={
                                            4
                                        }
                                        align="center"
                                    >
                                        No
                                        universities
                                        found
                                    </TableCell>
                                </TableRow>
                            ) : (
                                universities.map(
                                    (uni) => (
                                        <TableRow
                                            key={
                                                uni.id
                                            }
                                        >
                                            <TableCell>
                                                {
                                                    uni.name
                                                }
                                            </TableCell>
                                            <TableCell>
                                                {
                                                    uni.country
                                                }
                                            </TableCell>
                                            <TableCell>
                                                {
                                                    uni.city
                                                    || "—"
                                                }
                                            </TableCell>
                                            <TableCell>
                                                <Chip
                                                    label={
                                                        uni.is_active
                                                            ? "Active"
                                                            : "Inactive"
                                                    }
                                                    size="small"
                                                    color={
                                                        uni.is_active
                                                            ? "success"
                                                            : "default"
                                                    }
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

export default UniversitiesPage;
