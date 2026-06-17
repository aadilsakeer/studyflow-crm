import { useState } from "react";

import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    TextField,
} from "@mui/material";

import { createFollowUp } from "../services/followups";
import { showError, showSuccess } from "../utils/toast";

function FollowUpDialog({
    open,
    onClose,
    lead,
    onSuccess,
}) {
    const [date, setDate] =
        useState("");

    const [notes, setNotes] =
        useState("");

    async function handleSave() {
        if (!date) {
            showError("Follow up date is required");
            return;
        }

        try {
            await createFollowUp({
                lead: lead.id,
                follow_up_date:
                    date,
                notes,
            });

            setDate("");
            setNotes("");
            onClose();
            onSuccess?.();
            showSuccess("Follow up added");
        } catch (error) {
            console.error(error);
            showError("Failed to add follow up");
        }
    }

    if (!lead) return null;

    return (
        <Dialog
            open={open}
            onClose={onClose}
            maxWidth="sm"
            fullWidth
        >
            <DialogTitle>
                Add Follow Up
            </DialogTitle>

            <DialogContent>
                <TextField
                    type="datetime-local"
                    fullWidth
                    margin="normal"
                    value={date}
                    onChange={(e) =>
                        setDate(
                            e.target
                                .value
                        )
                    }
                />

                <TextField
                    label="Notes"
                    multiline
                    rows={4}
                    fullWidth
                    margin="normal"
                    value={notes}
                    onChange={(e) =>
                        setNotes(
                            e.target
                                .value
                        )
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
                    onClick={
                        handleSave
                    }
                >
                    Save
                </Button>
            </DialogActions>
        </Dialog>
    );
}

export default FollowUpDialog;