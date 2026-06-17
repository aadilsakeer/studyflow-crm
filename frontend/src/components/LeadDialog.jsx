import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    TextField,
    Button,
    MenuItem,
} from "@mui/material";

import { useState } from "react";
import { createLead, formatApiError } from "../services/leads";
import { showError, showSuccess } from "../utils/toast";

function LeadDialog({
    open,
    onClose,
    onSuccess,
}) {
    const [form, setForm] =
        useState({
            first_name: "",
            last_name: "",
            phone: "",
            email: "",
            country_interest: "",
            city: "",
            visa_type: "",
            status: "new",
            remarks: "",
        });

    async function handleSave() {
        if (!form.first_name.trim()) {
            showError("First name is required");
            return;
        }

        if (!form.phone.trim()) {
            showError("Phone is required");
            return;
        }

        try {
            await createLead({
                ...form,
                first_name: form.first_name.trim(),
                last_name: form.last_name.trim(),
                phone: form.phone.trim(),
                email: form.email.trim() || null,
            });

            setForm({
                first_name: "",
                last_name: "",
                phone: "",
                email: "",
                country_interest: "",
                city: "",
                visa_type: "",
                status: "new",
                remarks: "",
            });

            onSuccess();
            onClose();
            showSuccess("Lead created successfully");
        } catch (error) {
            console.error(error);
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
                Add New Lead
            </DialogTitle>

            <DialogContent>
                <TextField
                    label="First Name"
                    required
                    fullWidth
                    margin="normal"
                    value={
                        form.first_name
                    }
                    onChange={(e) =>
                        setForm({
                            ...form,
                            first_name:
                                e.target
                                    .value,
                        })
                    }
                />

                <TextField
                    label="Last Name"
                    fullWidth
                    margin="normal"
                    value={
                        form.last_name
                    }
                    onChange={(e) =>
                        setForm({
                            ...form,
                            last_name:
                                e.target
                                    .value,
                        })
                    }
                />

                <TextField
                    label="Phone"
                    required
                    fullWidth
                    margin="normal"
                    value={form.phone}
                    onChange={(e) =>
                        setForm({
                            ...form,
                            phone:
                                e.target
                                    .value,
                        })
                    }
                />

                <TextField
                    label="Email"
                    fullWidth
                    margin="normal"
                    value={form.email}
                    onChange={(e) =>
                        setForm({
                            ...form,
                            email:
                                e.target
                                    .value,
                        })
                    }
                />

                <TextField
                    label="Country Interest"
                    fullWidth
                    margin="normal"
                    value={
                        form.country_interest
                    }
                    onChange={(e) =>
                        setForm({
                            ...form,
                            country_interest:
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
                    label="Visa Type"
                    fullWidth
                    margin="normal"
                    value={
                        form.visa_type
                    }
                    onChange={(e) =>
                        setForm({
                            ...form,
                            visa_type:
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
                        form.status
                    }
                    onChange={(e) =>
                        setForm({
                            ...form,
                            status:
                                e.target
                                    .value,
                        })
                    }
                >
                    <MenuItem value="new">
                        New
                    </MenuItem>

                    <MenuItem value="contacted">
                        Contacted
                    </MenuItem>

                    <MenuItem value="interested">
                        Interested
                    </MenuItem>

                    <MenuItem value="follow_up">
                        Follow Up
                    </MenuItem>
                </TextField>

                <TextField
                    label="Remarks"
                    fullWidth
                    multiline
                    rows={3}
                    margin="normal"
                    value={
                        form.remarks
                    }
                    onChange={(e) =>
                        setForm({
                            ...form,
                            remarks:
                                e.target
                                    .value,
                        })
                    }
                />
            </DialogContent>

            <DialogActions>
                <Button
                    onClick={onClose}
                >
                    Cancel
                </Button>

                <Button
                    variant="contained"
                    onClick={handleSave}
                >
                    Save Lead
                </Button>
            </DialogActions>
        </Dialog>
    );
}

export default LeadDialog;