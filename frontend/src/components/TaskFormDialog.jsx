import { useEffect, useState } from "react";

import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    TextField,
    MenuItem,
    Grid,
} from "@mui/material";

import {
    TASK_TYPES,
    TASK_STATUSES,
    TASK_PRIORITIES,
    createTask,
    updateTask,
} from "../services/tasks";
import { showError, showSuccess } from "../utils/toast";

const EMPTY = {
    title: "",
    task_type: "general_task",
    status: "pending",
    priority: "medium",
    notes: "",
    description: "",
    due_date: "",
    reminder_at: "",
    assigned_to: "",
};

function TaskFormDialog({
    open,
    onClose,
    task,
    assignees = [],
    onSaved,
}) {
    const [form, setForm] = useState(EMPTY);
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        if (!open) return;

        if (task) {
            setForm({
                title: task.title || "",
                task_type: task.task_type || "general_task",
                status: task.status || "pending",
                priority: task.priority || "medium",
                notes: task.notes || "",
                description: task.description || "",
                due_date: task.due_date
                    ? task.due_date.slice(0, 16)
                    : "",
                reminder_at: task.reminder_at
                    ? task.reminder_at.slice(0, 16)
                    : "",
                assigned_to: task.assigned_to || "",
            });
        } else {
            setForm(EMPTY);
        }
    }, [open, task]);

    function handleChange(field) {
        return (event) => {
            setForm((prev) => ({
                ...prev,
                [field]: event.target.value,
            }));
        };
    }

    async function handleSubmit(event) {
        event.preventDefault();
        setSaving(true);

        const payload = {
            ...form,
            assigned_to: form.assigned_to || null,
            due_date: form.due_date || null,
            reminder_at: form.reminder_at || null,
        };

        try {
            if (task?.id) {
                await updateTask(task.id, payload);
                showSuccess("Task updated.");
            } else {
                await createTask(payload);
                showSuccess("Task created.");
            }

            onSaved?.();
            onClose();
        } catch (error) {
            showError(
                error.response?.data?.detail
                || "Failed to save task.",
            );
        } finally {
            setSaving(false);
        }
    }

    return (
        <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
            <form onSubmit={handleSubmit}>
                <DialogTitle>
                    {task ? "Edit Task" : "Create Task"}
                </DialogTitle>

                <DialogContent>
                    <Grid container spacing={2} sx={{ mt: 0.5 }}>
                        <Grid size={12}>
                            <TextField
                                label="Title"
                                value={form.title}
                                onChange={handleChange("title")}
                                required
                                fullWidth
                            />
                        </Grid>

                        <Grid size={6}>
                            <TextField
                                select
                                label="Type"
                                value={form.task_type}
                                onChange={handleChange("task_type")}
                                fullWidth
                            >
                                {TASK_TYPES.map((item) => (
                                    <MenuItem
                                        key={item.value}
                                        value={item.value}
                                    >
                                        {item.label}
                                    </MenuItem>
                                ))}
                            </TextField>
                        </Grid>

                        <Grid size={6}>
                            <TextField
                                select
                                label="Priority"
                                value={form.priority}
                                onChange={handleChange("priority")}
                                fullWidth
                            >
                                {TASK_PRIORITIES.map((item) => (
                                    <MenuItem
                                        key={item.value}
                                        value={item.value}
                                    >
                                        {item.label}
                                    </MenuItem>
                                ))}
                            </TextField>
                        </Grid>

                        <Grid size={6}>
                            <TextField
                                select
                                label="Status"
                                value={form.status}
                                onChange={handleChange("status")}
                                fullWidth
                            >
                                {TASK_STATUSES.map((item) => (
                                    <MenuItem
                                        key={item.value}
                                        value={item.value}
                                    >
                                        {item.label}
                                    </MenuItem>
                                ))}
                            </TextField>
                        </Grid>

                        <Grid size={6}>
                            <TextField
                                select
                                label="Assign To"
                                value={form.assigned_to}
                                onChange={handleChange("assigned_to")}
                                fullWidth
                            >
                                <MenuItem value="">Unassigned</MenuItem>
                                {assignees.map((user) => (
                                    <MenuItem
                                        key={user.id}
                                        value={user.id}
                                    >
                                        {user.display_name}
                                    </MenuItem>
                                ))}
                            </TextField>
                        </Grid>

                        <Grid size={6}>
                            <TextField
                                label="Due Date"
                                type="datetime-local"
                                value={form.due_date}
                                onChange={handleChange("due_date")}
                                fullWidth
                                InputLabelProps={{ shrink: true }}
                            />
                        </Grid>

                        <Grid size={6}>
                            <TextField
                                label="Reminder"
                                type="datetime-local"
                                value={form.reminder_at}
                                onChange={handleChange("reminder_at")}
                                fullWidth
                                InputLabelProps={{ shrink: true }}
                            />
                        </Grid>

                        <Grid size={12}>
                            <TextField
                                label="Notes"
                                value={form.notes}
                                onChange={handleChange("notes")}
                                fullWidth
                                multiline
                                minRows={2}
                            />
                        </Grid>
                    </Grid>
                </DialogContent>

                <DialogActions>
                    <Button onClick={onClose}>Cancel</Button>
                    <Button
                        type="submit"
                        variant="contained"
                        disabled={saving}
                    >
                        Save
                    </Button>
                </DialogActions>
            </form>
        </Dialog>
    );
}

export default TaskFormDialog;
