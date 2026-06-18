import { useCallback, useEffect, useState } from "react";

import {
    Box,
    Typography,
    TextField,
    Button,
    MenuItem,
    Stack,
    Divider,
} from "@mui/material";

import CommunicationHistory from "./CommunicationHistory";
import LoadingState from "./LoadingState";
import usePermissions from "../hooks/usePermissions";
import {
    getCommunicationHistory,
    createCommunicationNote,
    createEmailLog,
    createWhatsAppLog,
} from "../services/communications";
import { sendWhatsAppMessage } from "../services/whatsapp";
import { showError, showSuccess } from "../utils/toast";

function CommunicationHubPanel({
    leadId,
    studentId,
    defaultEmail = "",
    defaultPhone = "",
}) {
    const { can } = usePermissions();
    const [loading, setLoading] = useState(true);
    const [events, setEvents] = useState([]);
    const [note, setNote] = useState("");
    const [emailForm, setEmailForm] = useState({
        recipient_email: defaultEmail,
        subject: "",
        body: "",
        direction: "outbound",
    });
    const [whatsappForm, setWhatsAppForm] = useState({
        contact_number: defaultPhone,
        message: "",
        direction: "outbound",
    });

    const load = useCallback(async () => {
        setLoading(true);

        try {
            const params = {};

            if (leadId) params.lead = leadId;
            if (studentId) params.student = studentId;

            const data = await getCommunicationHistory(
                params,
            );
            setEvents(data.events || []);
        } catch {
            showError("Failed to load communication history.");
        } finally {
            setLoading(false);
        }
    }, [leadId, studentId]);

    useEffect(() => {
        load();
    }, [load]);

    useEffect(() => {
        setEmailForm((prev) => ({
            ...prev,
            recipient_email: defaultEmail || prev.recipient_email,
        }));
        setWhatsAppForm((prev) => ({
            ...prev,
            contact_number: defaultPhone || prev.contact_number,
        }));
    }, [defaultEmail, defaultPhone]);

    async function handleAddNote() {
        if (!note.trim()) return;

        try {
            await createCommunicationNote({
                lead: leadId || null,
                student: studentId || null,
                content: note.trim(),
            });
            setNote("");
            showSuccess("Note added.");
            load();
        } catch {
            showError("Failed to add note.");
        }
    }

    async function handleAddEmail() {
        try {
            await createEmailLog({
                lead: leadId || null,
                student: studentId || null,
                ...emailForm,
            });
            setEmailForm((prev) => ({
                ...prev,
                subject: "",
                body: "",
            }));
            showSuccess("Email logged.");
            load();
        } catch {
            showError("Failed to log email.");
        }
    }

    async function handleAddWhatsApp() {
        try {
            if (can("whatsapp.add")) {
                await sendWhatsAppMessage({
                    lead: leadId || null,
                    student: studentId || null,
                    recipient_number:
                        whatsappForm.contact_number,
                    message: whatsappForm.message,
                });
                showSuccess("WhatsApp sent via OpenWA.");
            } else {
                await createWhatsAppLog({
                    lead: leadId || null,
                    student: studentId || null,
                    ...whatsappForm,
                });
                showSuccess("WhatsApp logged.");
            }

            setWhatsAppForm((prev) => ({
                ...prev,
                message: "",
            }));
            load();
        } catch {
            showError("Failed to send WhatsApp.");
        }
    }

    if (loading) {
        return (
            <LoadingState message="Loading communications..." />
        );
    }

    return (
        <Box>
            <Typography variant="h6" fontWeight={600}>
                Communication Hub
            </Typography>

            {can("communications.add") && (
                <Stack spacing={2} sx={{ my: 2 }}>
                    <TextField
                        label="Add note"
                        value={note}
                        onChange={(e) =>
                            setNote(e.target.value)
                        }
                        multiline
                        minRows={2}
                        fullWidth
                    />
                    <Button
                        variant="outlined"
                        onClick={handleAddNote}
                    >
                        Save Note
                    </Button>

                    <Divider />

                    <TextField
                        label="Email recipient"
                        value={
                            emailForm.recipient_email
                        }
                        onChange={(e) =>
                            setEmailForm({
                                ...emailForm,
                                recipient_email:
                                    e.target.value,
                            })
                        }
                        fullWidth
                    />
                    <TextField
                        label="Email subject"
                        value={emailForm.subject}
                        onChange={(e) =>
                            setEmailForm({
                                ...emailForm,
                                subject: e.target.value,
                            })
                        }
                        fullWidth
                    />
                    <TextField
                        label="Email body"
                        value={emailForm.body}
                        onChange={(e) =>
                            setEmailForm({
                                ...emailForm,
                                body: e.target.value,
                            })
                        }
                        multiline
                        minRows={2}
                        fullWidth
                    />
                    <Button
                        variant="outlined"
                        onClick={handleAddEmail}
                    >
                        Log Email
                    </Button>

                    <Divider />

                    <TextField
                        label="WhatsApp number"
                        value={
                            whatsappForm.contact_number
                        }
                        onChange={(e) =>
                            setWhatsAppForm({
                                ...whatsappForm,
                                contact_number:
                                    e.target.value,
                            })
                        }
                        fullWidth
                    />
                    <TextField
                        label="WhatsApp message"
                        value={whatsappForm.message}
                        onChange={(e) =>
                            setWhatsAppForm({
                                ...whatsappForm,
                                message: e.target.value,
                            })
                        }
                        multiline
                        minRows={2}
                        fullWidth
                    />
                    <Button
                        variant="outlined"
                        onClick={handleAddWhatsApp}
                    >
                        {can("whatsapp.add")
                            ? "Send WhatsApp"
                            : "Log WhatsApp"}
                    </Button>
                </Stack>
            )}

            <CommunicationHistory events={events} />
        </Box>
    );
}

export default CommunicationHubPanel;
