import {
    Box,
    Typography,
    Chip,
    Stack,
} from "@mui/material";

const TYPE_COLORS = {
    call: "primary",
    note: "default",
    email: "secondary",
    whatsapp: "success",
};

const TYPE_LABELS = {
    call: "Call",
    note: "Note",
    email: "Email",
    whatsapp: "WhatsApp",
};

function formatTimestamp(value) {
    if (!value) return "—";

    return new Date(value).toLocaleString();
}

function CommunicationHistory({ events = [] }) {
    if (!events.length) {
        return (
            <Typography color="text.secondary">
                No communication history yet.
            </Typography>
        );
    }

    return (
        <Stack spacing={2}>
            {events.map((event) => (
                <Box
                    key={`${event.type}-${event.id}`}
                    sx={{
                        p: 2,
                        border: "1px solid #e5e7eb",
                        borderRadius: 2,
                    }}
                >
                    <Stack
                        direction="row"
                        spacing={1}
                        alignItems="center"
                        sx={{ mb: 1 }}
                    >
                        <Chip
                            label={
                                TYPE_LABELS[event.type]
                                || event.type
                            }
                            size="small"
                            color={
                                TYPE_COLORS[event.type]
                                || "default"
                            }
                        />
                        <Typography
                            variant="body2"
                            color="text.secondary"
                        >
                            {formatTimestamp(
                                event.timestamp,
                            )}
                        </Typography>
                    </Stack>

                    <Typography fontWeight={600}>
                        {event.title}
                    </Typography>

                    {event.summary && (
                        <Typography
                            variant="body2"
                            sx={{ mt: 0.5 }}
                        >
                            {event.summary}
                        </Typography>
                    )}

                    {event.author_name && (
                        <Typography
                            variant="caption"
                            color="text.secondary"
                            sx={{ mt: 1, display: "block" }}
                        >
                            by {event.author_name}
                        </Typography>
                    )}

                    {event.meta?.lead_name && (
                        <Typography
                            variant="caption"
                            color="text.secondary"
                        >
                            Lead: {event.meta.lead_name}
                        </Typography>
                    )}
                </Box>
            ))}
        </Stack>
    );
}

export default CommunicationHistory;
