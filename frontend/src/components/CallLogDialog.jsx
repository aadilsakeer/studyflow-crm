import { useState } from "react";

import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    TextField,
    MenuItem,
} from "@mui/material";

import { createCallLog } from "../services/calllogs";
import { showError, showSuccess } from "../utils/toast";

const OUTCOMES = [
    { value: "answered", label: "Answered" },
    { value: "not_answered", label: "Not Answered" },
    { value: "busy", label: "Busy" },
    { value: "wrong_number", label: "Wrong Number" },
    {
        value: "callback_requested",
        label: "Callback Requested",
    },
    { value: "interested", label: "Interested" },
    {
        value: "not_interested",
        label: "Not Interested",
    },
];

function CallLogDialog({
    open,
    onClose,
    lead,
    onSuccess,
}) {
    const [outcome, setOutcome] =
        useState("answered");

    const [notes, setNotes] =
        useState("");

    async function handleSave() {
        if (!outcome) {
            showError("Call outcome is required");
            return;
        }

        try {
            await createCallLog({
                lead: lead.id,
                outcome,
                notes,
            });

            setOutcome("answered");
            setNotes("");
            onClose();
            onSuccess?.();
            showSuccess("Call logged");
        } catch (error) {
            console.error(error);
            showError("Failed to log call");
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
                Log Call
            </DialogTitle>

            <DialogContent>
                <TextField
                    select
                    label="Outcome"
                    fullWidth
                    margin="normal"
                    value={outcome}
                    onChange={(e) =>
                        setOutcome(
                            e.target.value
                        )
                    }
                >
                    {OUTCOMES.map((item) => (
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
                    rows={4}
                    fullWidth
                    margin="normal"
                    value={notes}
                    onChange={(e) =>
                        setNotes(
                            e.target.value
                        )
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

export default CallLogDialog;
