import { useState, useEffect } from "react";

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
    updateApplication,
    deleteApplication,
} from "../services/applications";

import { formatApiError } from "../services/leads";
import {
    showError,
    showSuccess,
} from "../utils/toast";

const STATUS_OPTIONS = [
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

function ApplicationDrawer({
    open,
    onClose,
    application,
    onUpdated,
    onDeleted,
}) {
    const [editMode, setEditMode] =
        useState(false);

    const [form, setForm] = useState({
        university_name: "",
        course_name: "",
        intake: "",
        application_status: "draft",
        notes: "",
    });

    useEffect(() => {
        if (application) {
            setForm({
                university_name:
                    application.university_name
                    || "",
                course_name:
                    application.course_name
                    || "",
                intake:
                    application.intake || "",
                application_status:
                    application.application_status
                    || "draft",
                notes:
                    application.notes || "",
            });
            setEditMode(false);
        }
    }, [application]);

    if (!application) return null;

    async function handleSave() {
        try {
            await updateApplication(
                application.id,
                form
            );
            setEditMode(false);
            onUpdated?.();
            showSuccess(
                "Application updated"
            );
        } catch (error) {
            showError(formatApiError(error));
        }
    }

    async function handleDelete() {
        if (
            !window.confirm(
                "Delete this application?"
            )
        ) {
            return;
        }

        try {
            await deleteApplication(
                application.id
            );
            onDeleted?.();
            onClose();
            showSuccess(
                "Application deleted"
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
                    Application
                </Typography>

                <Typography
                    color="text.secondary"
                    sx={{ mt: 1 }}
                >
                    {application.student_code}{" "}
                    — {application.student_name}
                </Typography>

                <Chip
                    label={
                        form.application_status
                    }
                    color="primary"
                    sx={{ mt: 2 }}
                />

                <Divider sx={{ my: 3 }} />

                {editMode ? (
                    <>
                        <TextField
                            label="University"
                            fullWidth
                            margin="normal"
                            value={
                                form.university_name
                            }
                            onChange={(e) =>
                                setForm({
                                    ...form,
                                    university_name:
                                        e.target
                                            .value,
                                })
                            }
                        />

                        <TextField
                            label="Course"
                            fullWidth
                            margin="normal"
                            value={
                                form.course_name
                            }
                            onChange={(e) =>
                                setForm({
                                    ...form,
                                    course_name:
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
                            value={
                                form.application_status
                            }
                            onChange={(e) =>
                                setForm({
                                    ...form,
                                    application_status:
                                        e.target
                                            .value,
                                })
                            }
                        >
                            {STATUS_OPTIONS.map(
                                (item) => (
                                    <MenuItem
                                        key={
                                            item.value
                                        }
                                        value={
                                            item.value
                                        }
                                    >
                                        {
                                            item.label
                                        }
                                    </MenuItem>
                                )
                            )}
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
                        <Typography>
                            <strong>
                                University:
                            </strong>{" "}
                            {
                                application.university_name
                            }
                        </Typography>

                        <Typography sx={{ mt: 2 }}>
                            <strong>
                                Course:
                            </strong>{" "}
                            {
                                application.course_name
                            }
                        </Typography>

                        <Typography sx={{ mt: 2 }}>
                            <strong>
                                Intake:
                            </strong>{" "}
                            {application.intake
                                || "—"}
                        </Typography>

                        <Typography sx={{ mt: 2 }}>
                            <strong>
                                Notes:
                            </strong>
                        </Typography>

                        <Typography
                            color="text.secondary"
                        >
                            {application.notes
                                || "No notes"}
                        </Typography>

                        <Button
                            variant="contained"
                            fullWidth
                            sx={{ mt: 3 }}
                            onClick={() =>
                                setEditMode(true)
                            }
                        >
                            Edit Application
                        </Button>

                        <Button
                            variant="outlined"
                            color="error"
                            fullWidth
                            sx={{ mt: 2 }}
                            onClick={
                                handleDelete
                            }
                        >
                            Delete Application
                        </Button>
                    </>
                )}
            </Box>
        </Drawer>
    );
}

export default ApplicationDrawer;
