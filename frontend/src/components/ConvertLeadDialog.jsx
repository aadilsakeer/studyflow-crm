import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    Typography,
} from "@mui/material";

import { convertLead } from "../services/leads";
import { formatApiError } from "../services/leads";
import { showError, showSuccess } from "../utils/toast";

function ConvertLeadDialog({
    open,
    onClose,
    lead,
    onSuccess,
}) {
    async function handleConvert() {
        try {
            await convertLead(lead.id);
            onSuccess?.();
            onClose();
            showSuccess(
                "Lead converted to student"
            );
        } catch (error) {
            showError(formatApiError(error));
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
                Convert to Student
            </DialogTitle>

            <DialogContent>
                <Typography>
                    Convert{" "}
                    <strong>
                        {lead.first_name}{" "}
                        {lead.last_name}
                    </strong>{" "}
                    to a student record? The lead
                    status will be set to
                    converted.
                </Typography>
            </DialogContent>

            <DialogActions>
                <Button onClick={onClose}>
                    Cancel
                </Button>

                <Button
                    variant="contained"
                    onClick={handleConvert}
                >
                    Convert
                </Button>
            </DialogActions>
        </Dialog>
    );
}

export default ConvertLeadDialog;
