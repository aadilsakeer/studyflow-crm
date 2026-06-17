import {
    Box,
    Typography,
    Chip,
} from "@mui/material";

function LeadTimeline({ items }) {
    if (!items.length) {
        return (
            <Typography
                color="text.secondary"
                sx={{ mt: 1 }}
            >
                No activity yet
            </Typography>
        );
    }

    return (
        <Box sx={{ mt: 1 }}>
            {items.map((item) => (
                <Box
                    key={item.id}
                    sx={{
                        mt: 2,
                        pl: 2,
                        borderLeft:
                            "2px solid #E5E7EB",
                    }}
                >
                    <Box
                        sx={{
                            display: "flex",
                            alignItems: "center",
                            justifyContent:
                                "space-between",
                            gap: 1,
                        }}
                    >
                        <Typography
                            fontWeight={600}
                        >
                            {item.action}
                        </Typography>

                        <Chip
                            label={new Date(
                                item.created_at
                            ).toLocaleString()}
                            size="small"
                            variant="outlined"
                        />
                    </Box>

                    {item.description && (
                        <Typography
                            color="text.secondary"
                            sx={{ mt: 0.5 }}
                        >
                            {item.description}
                        </Typography>
                    )}

                    {item.performed_by_name && (
                        <Typography
                            variant="caption"
                            color="text.secondary"
                        >
                            by{" "}
                            {
                                item.performed_by_name
                            }
                        </Typography>
                    )}
                </Box>
            ))}
        </Box>
    );
}

export default LeadTimeline;
