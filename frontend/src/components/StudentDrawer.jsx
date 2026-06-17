import { useState, useEffect } from "react";

import ApplicationDialog from "./ApplicationDialog";

import {
    Drawer,
    Box,
    Typography,
    Divider,
    Chip,
    TextField,
    Button,
    MenuItem,
} from "@mui/material";

import {
    updateStudent,
} from "../services/students";

import {
    getStudentApplications,
} from "../services/applications";

import {
    formatApiError,
} from "../services/leads";

import {
    showError,
    showSuccess,
} from "../utils/toast";

function StudentDrawer({
    open,
    onClose,
    student,
    onUpdated,
}) {
    const [editMode, setEditMode] =
        useState(false);

    const [appDialogOpen,
        setAppDialogOpen] =
        useState(false);

    const [applications,
        setApplications] =
        useState([]);

    const [form, setForm] = useState({
        destination_country: "",
        preferred_university: "",
        intake: "",
        status: "counselling",
        notes: "",
    });

    useEffect(() => {
        if (student) {
            setForm({
                destination_country:
                    student.destination_country
                    || "",
                preferred_university:
                    student.preferred_university
                    || "",
                intake:
                    student.intake || "",
                status:
                    student.status
                    || "counselling",
                notes:
                    student.notes || "",
            });
            setEditMode(false);

            loadApplications(
                student.id
            );
        }
    }, [student]);

    async function loadApplications(
        studentId
    ) {
        try {
            const data =
                await getStudentApplications(
                    studentId
                );
            setApplications(data);
        } catch (error) {
            console.error(error);
        }
    }

    if (!student) return null;

    async function handleSave() {
        try {
            await updateStudent(
                student.id,
                form
            );
            setEditMode(false);
            onUpdated?.();
            showSuccess(
                "Student updated successfully"
            );
        } catch (error) {
            showError(formatApiError(error));
        }
    }

    return (
        <Drawer
            anchor="right"
            open={open}
            onClose={onClose}
        >
            <ApplicationDialog
                open={appDialogOpen}
                onClose={() =>
                    setAppDialogOpen(false)
                }
                student={student}
                onSuccess={() =>
                    loadApplications(
                        student.id
                    )
                }
            />

            <Box
                sx={{
                    width: 420,
                    p: 3,
                    overflowY: "auto",
                    maxHeight: "100vh",
                }}
            >
                <Typography
                    variant="h5"
                    fontWeight={700}
                >
                    {student.lead_name}
                </Typography>

                <Typography
                    color="text.secondary"
                    sx={{ mt: 1 }}
                >
                    {student.student_id}
                </Typography>

                <Chip
                    label={form.status}
                    color="primary"
                    sx={{ mt: 2 }}
                />

                <Divider sx={{ my: 3 }} />

                <Typography>
                    <strong>Phone:</strong>{" "}
                    {student.lead_phone}
                </Typography>

                <Typography sx={{ mt: 2 }}>
                    <strong>Email:</strong>{" "}
                    {student.lead_email || "—"}
                </Typography>

                {editMode ? (
                    <>
                        <TextField
                            label="Destination Country"
                            fullWidth
                            margin="normal"
                            value={
                                form.destination_country
                            }
                            onChange={(e) =>
                                setForm({
                                    ...form,
                                    destination_country:
                                        e.target
                                            .value,
                                })
                            }
                        />

                        <TextField
                            label="Preferred University"
                            fullWidth
                            margin="normal"
                            value={
                                form.preferred_university
                            }
                            onChange={(e) =>
                                setForm({
                                    ...form,
                                    preferred_university:
                                        e.target
                                            .value,
                                })
                            }
                        />

                        <TextField
                            label="Intake"
                            fullWidth
                            margin="normal"
                            value={form.intake}
                            onChange={(e) =>
                                setForm({
                                    ...form,
                                    intake:
                                        e.target
                                            .value,
                                })
                            }
                        />

                        <TextField
                            select
                            label="Status"
                            fullWidth
                            margin="normal"
                            value={form.status}
                            onChange={(e) =>
                                setForm({
                                    ...form,
                                    status:
                                        e.target
                                            .value,
                                })
                            }
                        >
                            <MenuItem value="counselling">
                                Counselling
                            </MenuItem>
                            <MenuItem value="application">
                                Application
                            </MenuItem>
                            <MenuItem value="offer_received">
                                Offer Received
                            </MenuItem>
                            <MenuItem value="visa_processing">
                                Visa Processing
                            </MenuItem>
                            <MenuItem value="visa_approved">
                                Visa Approved
                            </MenuItem>
                            <MenuItem value="enrolled">
                                Enrolled
                            </MenuItem>
                            <MenuItem value="closed">
                                Closed
                            </MenuItem>
                        </TextField>

                        <TextField
                            label="Notes"
                            multiline
                            rows={4}
                            fullWidth
                            margin="normal"
                            value={form.notes}
                            onChange={(e) =>
                                setForm({
                                    ...form,
                                    notes:
                                        e.target
                                            .value,
                                })
                            }
                        />

                        <Button
                            variant="contained"
                            fullWidth
                            sx={{ mt: 2 }}
                            onClick={handleSave}
                        >
                            Save Changes
                        </Button>
                    </>
                ) : (
                    <>
                        <Typography sx={{ mt: 2 }}>
                            <strong>
                                Country:
                            </strong>{" "}
                            {
                                student.destination_country
                                || "—"
                            }
                        </Typography>

                        <Typography sx={{ mt: 2 }}>
                            <strong>
                                University:
                            </strong>{" "}
                            {
                                student.preferred_university
                                || "—"
                            }
                        </Typography>

                        <Typography sx={{ mt: 2 }}>
                            <strong>
                                Intake:
                            </strong>{" "}
                            {student.intake || "—"}
                        </Typography>

                        <Typography sx={{ mt: 2 }}>
                            <strong>
                                Notes:
                            </strong>
                        </Typography>

                        <Typography
                            color="text.secondary"
                        >
                            {student.notes
                                || "No notes"}
                        </Typography>

                        <Divider sx={{ my: 3 }} />

                        <Typography
                            variant="h6"
                            fontWeight={600}
                        >
                            Applications
                        </Typography>

                        {applications.length
                        === 0 ? (
                            <Typography
                                color="text.secondary"
                                sx={{ mt: 1 }}
                            >
                                No applications
                                yet
                            </Typography>
                        ) : (
                            applications.map(
                                (app) => (
                                    <Box
                                        key={
                                            app.id
                                        }
                                        sx={{
                                            mt: 2,
                                            p: 2,
                                            border:
                                                "1px solid #E5E7EB",
                                            borderRadius: 2,
                                        }}
                                    >
                                        <Typography
                                            fontWeight={
                                                600
                                            }
                                        >
                                            {
                                                app.university_name
                                            }
                                        </Typography>
                                        <Typography
                                            variant="body2"
                                            color="text.secondary"
                                        >
                                            {
                                                app.course_name
                                            }
                                        </Typography>
                                        <Chip
                                            label={
                                                app.application_status
                                            }
                                            size="small"
                                            sx={{
                                                mt: 1,
                                            }}
                                        />
                                    </Box>
                                )
                            )
                        )}

                        <Button
                            variant="outlined"
                            fullWidth
                            sx={{ mt: 2 }}
                            onClick={() =>
                                setAppDialogOpen(
                                    true
                                )
                            }
                        >
                            New Application
                        </Button>

                        <Button
                            variant="contained"
                            fullWidth
                            sx={{ mt: 2 }}
                            onClick={() =>
                                setEditMode(true)
                            }
                        >
                            Edit Student
                        </Button>
                    </>
                )}
            </Box>
        </Drawer>
    );
}

export default StudentDrawer;
