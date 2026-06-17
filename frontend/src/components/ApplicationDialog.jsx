import { useState, useEffect } from "react";

import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    TextField,
    MenuItem,
} from "@mui/material";

import { createApplication } from "../services/applications";
import { getStudents } from "../services/students";
import { getUniversities } from "../services/universities";
import { formatApiError } from "../services/leads";
import { showError, showSuccess } from "../utils/toast";

const STATUSES = [
    { value: "draft", label: "Draft" },
    {
        value: "submitted",
        label: "Submitted",
    },
];

function ApplicationDialog({
    open,
    onClose,
    onSuccess,
    student,
}) {
    const [students, setStudents] =
        useState([]);
    const [universities, setUniversities] =
        useState([]);

    const [form, setForm] = useState({
        student: "",
        university_name: "",
        course_name: "",
        intake: "",
        application_status: "draft",
        notes: "",
    });

    useEffect(() => {
        if (open) {
            loadOptions();
            setForm({
                student: student?.id || "",
                university_name: "",
                course_name: "",
                intake: student?.intake || "",
                application_status: "draft",
                notes: "",
            });
        }
    }, [open, student]);

    async function loadOptions() {
        try {
            const [studentData, uniData] =
                await Promise.all([
                    getStudents(),
                    getUniversities(),
                ]);

            setStudents(
                Array.isArray(studentData)
                    ? studentData
                    : studentData.results
                    || []
            );
            setUniversities(
                Array.isArray(uniData)
                    ? uniData
                    : uniData.results
                    || []
            );
        } catch (error) {
            console.error(error);
        }
    }

    function handleUniversityPick(name) {
        setForm({
            ...form,
            university_name: name,
        });
    }

    async function handleSave() {
        if (!form.student) {
            showError("Student is required");
            return;
        }

        if (!form.university_name.trim()) {
            showError(
                "University is required"
            );
            return;
        }

        if (!form.course_name.trim()) {
            showError("Course is required");
            return;
        }

        try {
            await createApplication({
                ...form,
                student: Number(form.student),
            });

            onSuccess?.();
            onClose();
            showSuccess(
                "Application created"
            );
        } catch (error) {
            showError(formatApiError(error));
        }
    }

    return (
        <Dialog
            open={open}
            onClose={onClose}
            maxWidth="md"
            fullWidth
        >
            <DialogTitle>
                New Application
            </DialogTitle>

            <DialogContent>
                <TextField
                    select
                    label="Student"
                    fullWidth
                    margin="normal"
                    value={form.student}
                    onChange={(e) =>
                        setForm({
                            ...form,
                            student:
                                e.target.value,
                        })
                    }
                    disabled={!!student}
                >
                    {students.map((item) => (
                        <MenuItem
                            key={item.id}
                            value={item.id}
                        >
                            {item.student_id}{" "}
                            — {item.lead_name}
                        </MenuItem>
                    ))}
                </TextField>

                <TextField
                    select
                    label="University (from catalog)"
                    fullWidth
                    margin="normal"
                    value=""
                    onChange={(e) =>
                        handleUniversityPick(
                            e.target.value
                        )
                    }
                    helperText="Pick from catalog or type below"
                >
                    <MenuItem value="">
                        Select university
                    </MenuItem>
                    {universities.map((uni) => (
                        <MenuItem
                            key={uni.id}
                            value={uni.name}
                        >
                            {uni.name} (
                            {uni.country})
                        </MenuItem>
                    ))}
                </TextField>

                <TextField
                    label="University Name"
                    required
                    fullWidth
                    margin="normal"
                    value={
                        form.university_name
                    }
                    onChange={(e) =>
                        setForm({
                            ...form,
                            university_name:
                                e.target.value,
                        })
                    }
                />

                <TextField
                    label="Course Name"
                    required
                    fullWidth
                    margin="normal"
                    value={form.course_name}
                    onChange={(e) =>
                        setForm({
                            ...form,
                            course_name:
                                e.target.value,
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
                                e.target.value,
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
                                e.target.value,
                        })
                    }
                >
                    {STATUSES.map((item) => (
                        <MenuItem
                            key={item.value}
                            value={item.value}
                        >
                            {item.label}
                        </MenuItem>
                    ))}
                </TextField>

                <TextField
                    label="Notes"
                    multiline
                    rows={3}
                    fullWidth
                    margin="normal"
                    value={form.notes}
                    onChange={(e) =>
                        setForm({
                            ...form,
                            notes:
                                e.target.value,
                        })
                    }
                />
            </DialogContent>

            <DialogActions>
                <Button onClick={onClose}>
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
    );
}

export default ApplicationDialog;
