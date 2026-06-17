import { useState, useEffect } from "react";

import FollowUpDialog from "./FollowUpDialog";
import CallLogDialog from "./CallLogDialog";
import ConvertLeadDialog from "./ConvertLeadDialog";
import LeadTimeline from "./LeadTimeline";
import LeadAuditLog from "./LeadAuditLog";

import {
    Drawer,
    Box,
    Typography,
    Divider,
    Chip,
    TextField,
    Button,
    MenuItem,
    Checkbox,
    FormControlLabel,
} from "@mui/material";

import {
    updateLead,
    deleteLead,
    formatApiError,
} from "../services/leads";

import {
    getLeadFollowUps,
    updateFollowUp,
} from "../services/followups";

import {
    getLeadCallLogs,
} from "../services/calllogs";

import {
    getLeadTimeline,
} from "../services/timeline";

import {
    getLeadAuditLogs,
} from "../services/audit";

import {
    showError,
    showSuccess,
} from "../utils/toast";

function LeadDrawer({
    open,
    onClose,
    lead,
    onLeadUpdated,
    onLeadDeleted,
}) {
    const [editMode, setEditMode] =
        useState(false);

    const [followUpOpen,
        setFollowUpOpen] =
        useState(false);

    const [callLogOpen,
        setCallLogOpen] =
        useState(false);

    const [convertOpen,
        setConvertOpen] =
        useState(false);

    const [followUps,
        setFollowUps] =
        useState([]);

    const [callLogs,
        setCallLogs] =
        useState([]);

    const [timeline,
        setTimeline] =
        useState([]);

    const [auditLogs,
        setAuditLogs] =
        useState([]);

    const [form, setForm] =
        useState({
            country_interest: "",
            city: "",
            visa_type: "",
            status: "",
            remarks: "",
        });

    useEffect(() => {
        if (lead) {
            setForm({
                country_interest:
                    lead.country_interest || "",
                city:
                    lead.city || "",
                visa_type:
                    lead.visa_type || "",
                status:
                    lead.status || "new",
                remarks:
                    lead.remarks || "",
            });

            setEditMode(false);

            loadLeadActivity(
                lead.id
            );
        }
    }, [lead]);

    async function loadLeadActivity(
        leadId
    ) {
        try {
            const [
                followUpData,
                callLogData,
                timelineData,
                auditData,
            ] = await Promise.all([
                getLeadFollowUps(leadId),
                getLeadCallLogs(leadId),
                getLeadTimeline(leadId),
                getLeadAuditLogs(leadId),
            ]);

            setFollowUps(followUpData);
            setCallLogs(callLogData);
            setTimeline(timelineData);
            setAuditLogs(auditData);
        } catch (error) {
            console.error(error);
        }
    }

    async function loadFollowUps(
        leadId
    ) {
        loadLeadActivity(leadId);
    }

    async function handleToggleComplete(
        followUp
    ) {
        try {
            await updateFollowUp(
                followUp.id,
                {
                    completed:
                        !followUp.completed,
                }
            );

            loadFollowUps(lead.id);
        } catch (error) {
            console.error(error);
            showError("Failed to update follow up");
        }
    }

    function formatOutcome(value) {
        return value
            .replace(/_/g, " ")
            .replace(/\b\w/g, (c) =>
                c.toUpperCase()
            );
    }

    if (!lead) return null;

    async function handleSave() {
        try {
            const updated = await updateLead(
                lead.id,
                form
            );

            setEditMode(false);
            onLeadUpdated?.(updated);
            loadLeadActivity(lead.id);
            showSuccess("Lead updated successfully");
        } catch (error) {
            console.error(error);
            showError(formatApiError(error));
        }
    }

    async function handleDelete() {
        const confirmed =
            window.confirm(
                "Delete this lead?"
            );

        if (!confirmed) return;

        try {
            await deleteLead(
                lead.id
            );

            onLeadDeleted?.();
            onClose();
            showSuccess("Lead deleted successfully");
        } catch (error) {
            console.error(error);
            showError(formatApiError(error));
        }
    }

    return (
        <>
            <FollowUpDialog
                open={followUpOpen}
                onClose={() =>
                    setFollowUpOpen(false)
                }
                lead={lead}
                onSuccess={() =>
                    loadLeadActivity(lead.id)
                }
            />

            <CallLogDialog
                open={callLogOpen}
                onClose={() =>
                    setCallLogOpen(false)
                }
                lead={lead}
                onSuccess={() =>
                    loadLeadActivity(lead.id)
                }
            />

            <ConvertLeadDialog
                open={convertOpen}
                onClose={() =>
                    setConvertOpen(false)
                }
                lead={lead}
                onSuccess={() => {
                    loadLeadActivity(lead.id);
                    onLeadUpdated?.({
                        ...lead,
                        status: "converted",
                    });
                }}
            />

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
                        {lead.first_name}{" "}
                        {lead.last_name}
                    </Typography>

                    <Chip
                        label={form.status}
                        color="success"
                        sx={{ mt: 2 }}
                    />

                    <Divider sx={{ my: 3 }} />

                    <Typography>
                        <strong>Phone:</strong>{" "}
                        {lead.phone}
                    </Typography>

                    <Typography sx={{ mt: 2 }}>
                        <strong>Email:</strong>{" "}
                        {lead.email}
                    </Typography>

                    {editMode ? (
                        <>
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
                                            e.target.value,
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
                                            e.target.value,
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
                                            e.target.value,
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
                                            e.target.value,
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

                                <MenuItem value="converted">
                                    Converted
                                </MenuItem>

                                <MenuItem value="lost">
                                    Lost
                                </MenuItem>
                            </TextField>

                            <TextField
                                label="Remarks"
                                multiline
                                rows={4}
                                fullWidth
                                margin="normal"
                                value={form.remarks}
                                onChange={(e) =>
                                    setForm({
                                        ...form,
                                        remarks:
                                            e.target.value,
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
                                {lead.country_interest}
                            </Typography>

                            <Typography sx={{ mt: 2 }}>
                                <strong>
                                    City:
                                </strong>{" "}
                                {lead.city}
                            </Typography>

                            <Typography sx={{ mt: 2 }}>
                                <strong>
                                    Visa Type:
                                </strong>{" "}
                                {lead.visa_type}
                            </Typography>

                            <Typography sx={{ mt: 2 }}>
                                <strong>
                                    Remarks:
                                </strong>
                            </Typography>

                            <Typography color="text.secondary">
                                {lead.remarks ||
                                    "No Remarks"}
                            </Typography>

                            <Divider sx={{ my: 3 }} />

                            <Typography
                                variant="h6"
                                fontWeight={600}
                            >
                                Follow Ups
                            </Typography>

                            {followUps.length === 0 ? (
                                <Typography
                                    color="text.secondary"
                                    sx={{ mt: 1 }}
                                >
                                    No Follow Ups
                                </Typography>
                            ) : (
                                followUps.map(
                                    (item) => (
                                        <Box
                                            key={item.id}
                                            sx={{
                                                mt: 2,
                                                p: 2,
                                                border:
                                                    "1px solid #E5E7EB",
                                                borderRadius: 2,
                                                opacity:
                                                    item.completed
                                                        ? 0.75
                                                        : 1,
                                                bgcolor:
                                                    item.completed
                                                        ? "#F0FDF4"
                                                        : "transparent",
                                            }}
                                        >
                                            <Box
                                                sx={{
                                                    display:
                                                        "flex",
                                                    alignItems:
                                                        "center",
                                                    justifyContent:
                                                        "space-between",
                                                    gap: 1,
                                                }}
                                            >
                                                <Typography
                                                    fontWeight={600}
                                                    sx={{
                                                        textDecoration:
                                                            item.completed
                                                                ? "line-through"
                                                                : "none",
                                                    }}
                                                >
                                                    {new Date(
                                                        item.follow_up_date
                                                    ).toLocaleString()}
                                                </Typography>

                                                <Chip
                                                    label={
                                                        item.completed
                                                            ? "Completed"
                                                            : "Pending"
                                                    }
                                                    size="small"
                                                    color={
                                                        item.completed
                                                            ? "success"
                                                            : "default"
                                                    }
                                                />
                                            </Box>

                                            {item.notes && (
                                                <Typography
                                                    color="text.secondary"
                                                    sx={{
                                                        mt: 1,
                                                    }}
                                                >
                                                    {
                                                        item.notes
                                                    }
                                                </Typography>
                                            )}

                                            <FormControlLabel
                                                control={
                                                    <Checkbox
                                                        checked={
                                                            item.completed
                                                        }
                                                        onChange={() =>
                                                            handleToggleComplete(
                                                                item
                                                            )
                                                        }
                                                        size="small"
                                                    />
                                                }
                                                label="Mark complete"
                                                sx={{
                                                    mt: 1,
                                                    ml: 0,
                                                }}
                                            />
                                        </Box>
                                    )
                                )
                            )}

                            <Divider sx={{ my: 3 }} />

                            <Typography
                                variant="h6"
                                fontWeight={600}
                            >
                                Call Logs
                            </Typography>

                            {callLogs.length === 0 ? (
                                <Typography
                                    color="text.secondary"
                                    sx={{ mt: 1 }}
                                >
                                    No calls logged
                                </Typography>
                            ) : (
                                callLogs.map(
                                    (item) => (
                                        <Box
                                            key={item.id}
                                            sx={{
                                                mt: 2,
                                                p: 2,
                                                border:
                                                    "1px solid #E5E7EB",
                                                borderRadius: 2,
                                            }}
                                        >
                                            <Box
                                                sx={{
                                                    display:
                                                        "flex",
                                                    alignItems:
                                                        "center",
                                                    justifyContent:
                                                        "space-between",
                                                    gap: 1,
                                                }}
                                            >
                                                <Chip
                                                    label={formatOutcome(
                                                        item.outcome
                                                    )}
                                                    size="small"
                                                    color="primary"
                                                />

                                                <Typography
                                                    variant="caption"
                                                    color="text.secondary"
                                                >
                                                    {new Date(
                                                        item.call_time
                                                    ).toLocaleString()}
                                                </Typography>
                                            </Box>

                                            {item.notes && (
                                                <Typography
                                                    color="text.secondary"
                                                    sx={{
                                                        mt: 1,
                                                    }}
                                                >
                                                    {
                                                        item.notes
                                                    }
                                                </Typography>
                                            )}

                                            {item.called_by_name && (
                                                <Typography
                                                    variant="caption"
                                                    color="text.secondary"
                                                    display="block"
                                                    sx={{
                                                        mt: 0.5,
                                                    }}
                                                >
                                                    by{" "}
                                                    {
                                                        item.called_by_name
                                                    }
                                                </Typography>
                                            )}
                                        </Box>
                                    )
                                )
                            )}

                            <Divider sx={{ my: 3 }} />

                            <Typography
                                variant="h6"
                                fontWeight={600}
                            >
                                Activity Timeline
                            </Typography>

                            <LeadTimeline
                                items={timeline}
                            />

                            <Divider sx={{ my: 3 }} />

                            <Typography
                                variant="h6"
                                fontWeight={600}
                            >
                                Audit Log
                            </Typography>

                            <LeadAuditLog
                                items={auditLogs}
                            />

                            <Button
                                variant="contained"
                                fullWidth
                                sx={{ mt: 3 }}
                                onClick={() =>
                                    setEditMode(true)
                                }
                            >
                                Edit Lead
                            </Button>

                            <Button
                                variant="outlined"
                                fullWidth
                                sx={{ mt: 2 }}
                                onClick={() =>
                                    setCallLogOpen(
                                        true
                                    )
                                }
                            >
                                Log Call
                            </Button>

                            {lead.status
                                !== "converted" && (
                                <Button
                                    variant="contained"
                                    color="secondary"
                                    fullWidth
                                    sx={{ mt: 2 }}
                                    onClick={() =>
                                        setConvertOpen(
                                            true
                                        )
                                    }
                                >
                                    Convert to
                                    Student
                                </Button>
                            )}

                            <Button
                                variant="outlined"
                                color="error"
                                fullWidth
                                sx={{ mt: 2 }}
                                onClick={
                                    handleDelete
                                }
                            >
                                Delete Lead
                            </Button>

                            <Button
                                variant="outlined"
                                fullWidth
                                sx={{ mt: 2 }}
                                onClick={() =>
                                    setFollowUpOpen(
                                        true
                                    )
                                }
                            >
                                Add Follow Up
                            </Button>
                        </>
                    )}
                </Box>
            </Drawer>
        </>
    );
}

export default LeadDrawer;