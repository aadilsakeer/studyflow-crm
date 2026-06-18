import { useCallback, useEffect, useState } from "react";

import {
    Paper,
    Typography,
    TextField,
    Button,
    Box,
    Alert,
    Chip,
} from "@mui/material";

import LoadingState from "../components/LoadingState";
import usePermissions from "../hooks/usePermissions";
import {
    getWhatsAppServer,
    updateWhatsAppServer,
    getWhatsAppSessionStatus,
    connectWhatsAppSession,
    getWhatsAppQR,
    getWhatsAppMessages,
} from "../services/whatsapp";
import { showError, showSuccess } from "../utils/toast";

function WhatsAppPage() {
    const { can } = usePermissions();
    const [loading, setLoading] = useState(true);
    const [serverForm, setServerForm] = useState({
        base_url: "",
        api_key: "",
        is_active: true,
    });
    const [session, setSession] = useState(null);
    const [qrData, setQrData] = useState(null);
    const [messages, setMessages] = useState([]);

    const load = useCallback(async () => {
        setLoading(true);

        try {
            const [serverData, statusData, messageData] =
                await Promise.all([
                    getWhatsAppServer(),
                    getWhatsAppSessionStatus(),
                    getWhatsAppMessages(),
                ]);

            setServerForm({
                base_url: serverData.base_url || "",
                api_key: "",
                is_active: serverData.is_active ?? true,
            });
            setSession(statusData);
            setMessages(messageData.slice(0, 20));
        } catch {
            showError("Failed to load WhatsApp settings.");
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        load();
    }, [load]);

    async function handleSaveServer() {
        try {
            const payload = {
                base_url: serverForm.base_url,
                is_active: serverForm.is_active,
            };

            if (serverForm.api_key) {
                payload.api_key = serverForm.api_key;
            }

            await updateWhatsAppServer(payload);
            showSuccess("OpenWA server settings saved.");
            load();
        } catch {
            showError("Failed to save server settings.");
        }
    }

    async function handleConnect() {
        try {
            const data = await connectWhatsAppSession();
            setQrData(data.qr);
            setSession({
                connected: data.is_connected,
                session_id: data.session_id,
            });
            showSuccess("WhatsApp session started. Scan the QR code.");
        } catch {
            showError("Failed to start WhatsApp session.");
        }
    }

    async function handleRefreshQR() {
        try {
            const data = await getWhatsAppQR();
            setQrData(data.qr);
        } catch {
            showError("QR code not available yet.");
        }
    }

    async function handleRefreshStatus() {
        try {
            const data = await getWhatsAppSessionStatus();
            setSession(data);
        } catch {
            showError("Failed to refresh session status.");
        }
    }

    if (loading) {
        return <LoadingState message="Loading WhatsApp..." />;
    }

    const qrValue =
        qrData?.qr
        || qrData?.data
        || qrData?.image
        || qrData?.value
        || null;

    return (
        <Box>
            <Typography variant="h4" fontWeight={700} sx={{ mb: 3 }}>
                WhatsApp (OpenWA)
            </Typography>

            <Alert severity="info" sx={{ mb: 3 }}>
                Connect to your self-hosted{" "}
                <a
                    href="https://www.open-wa.org/"
                    target="_blank"
                    rel="noreferrer"
                >
                    OpenWA
                </a>{" "}
                gateway. Default API URL: http://localhost:2785/api
            </Alert>

            {can("whatsapp.change") && (
                <Paper sx={{ p: 3, mb: 3, borderRadius: 4 }}>
                    <Typography variant="h6" sx={{ mb: 2 }}>
                        OpenWA Server
                    </Typography>
                    <TextField
                        label="Base URL"
                        value={serverForm.base_url}
                        onChange={(e) =>
                            setServerForm({
                                ...serverForm,
                                base_url: e.target.value,
                            })
                        }
                        fullWidth
                        sx={{ mb: 2 }}
                        placeholder="http://localhost:2785/api"
                    />
                    <TextField
                        label="API Key"
                        type="password"
                        value={serverForm.api_key}
                        onChange={(e) =>
                            setServerForm({
                                ...serverForm,
                                api_key: e.target.value,
                            })
                        }
                        fullWidth
                        sx={{ mb: 2 }}
                        placeholder="Leave blank to keep existing key"
                    />
                    <Button
                        variant="contained"
                        onClick={handleSaveServer}
                    >
                        Save Server Settings
                    </Button>
                </Paper>
            )}

            <Paper sx={{ p: 3, mb: 3, borderRadius: 4 }}>
                <Typography variant="h6" sx={{ mb: 2 }}>
                    Session
                </Typography>

                <Chip
                    label={
                        session?.connected
                            ? "Connected"
                            : "Not connected"
                    }
                    color={
                        session?.connected
                            ? "success"
                            : "default"
                    }
                    sx={{ mb: 2 }}
                />

                {can("whatsapp.add") && (
                    <Box sx={{ display: "flex", gap: 2, mb: 2 }}>
                        <Button
                            variant="contained"
                            onClick={handleConnect}
                        >
                            Connect / Start Session
                        </Button>
                        <Button
                            variant="outlined"
                            onClick={handleRefreshQR}
                        >
                            Refresh QR
                        </Button>
                        <Button
                            variant="outlined"
                            onClick={handleRefreshStatus}
                        >
                            Refresh Status
                        </Button>
                    </Box>
                )}

                {qrValue && (
                    <Box sx={{ mt: 2 }}>
                        <Typography sx={{ mb: 1 }}>
                            Scan this QR in WhatsApp:
                        </Typography>
                        {typeof qrValue === "string"
                        && qrValue.startsWith("data:image") ? (
                            <img
                                src={qrValue}
                                alt="WhatsApp QR"
                                style={{ maxWidth: 280 }}
                            />
                        ) : (
                            <Typography
                                component="pre"
                                sx={{
                                    p: 2,
                                    bgcolor: "#f8fafc",
                                    borderRadius: 2,
                                    overflow: "auto",
                                }}
                            >
                                {JSON.stringify(qrData, null, 2)}
                            </Typography>
                        )}
                    </Box>
                )}
            </Paper>

            <Paper sx={{ p: 3, borderRadius: 4 }}>
                <Typography variant="h6" sx={{ mb: 2 }}>
                    Recent Messages
                </Typography>
                {messages.length === 0 ? (
                    <Typography color="text.secondary">
                        No messages sent yet.
                    </Typography>
                ) : (
                    messages.map((item) => (
                        <Box
                            key={item.id}
                            sx={{
                                mb: 2,
                                p: 2,
                                border: "1px solid #e5e7eb",
                                borderRadius: 2,
                            }}
                        >
                            <Typography fontWeight={600}>
                                {item.recipient_number}
                            </Typography>
                            <Typography variant="body2">
                                {item.message}
                            </Typography>
                            <Chip
                                label={item.status}
                                size="small"
                                sx={{ mt: 1 }}
                            />
                        </Box>
                    ))
                )}
            </Paper>
        </Box>
    );
}

export default WhatsAppPage;
