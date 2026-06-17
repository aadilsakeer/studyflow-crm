import {
    Paper,
    Typography,
    List,
    ListItem,
    ListItemText,
    Box,
    Chip,
} from "@mui/material";

function formatWhen(isoString) {
    if (!isoString) return "";

    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(
        diffMs / 60000
    );

    if (diffMins < 1) return "Just now";
    if (diffMins < 60) {
        return `${diffMins}m ago`;
    }

    const diffHours = Math.floor(
        diffMins / 60
    );

    if (diffHours < 24) {
        return `${diffHours}h ago`;
    }

    return date.toLocaleString();
}

function RecentActivities({
    activities = [],
}) {
    return (
        <Paper
            elevation={0}
            sx={{
                p: 3,
                borderRadius: 4,
                border: "1px solid #E5E7EB",
                backgroundColor: "#FFFFFF",
                height: "100%",
                minHeight: 420,
            }}
        >
            <Typography
                variant="h6"
                sx={{
                    mb: 1,
                    fontWeight: 600,
                }}
            >
                Recent Activities
            </Typography>

            <Typography
                variant="body2"
                color="text.secondary"
                sx={{ mb: 2 }}
            >
                Latest CRM activity across leads
            </Typography>

            {activities.length === 0 ? (
                <Box
                    sx={{
                        py: 6,
                        textAlign: "center",
                    }}
                >
                    <Typography
                        color="text.secondary"
                    >
                        No activity yet. Actions
                        on leads will appear here.
                    </Typography>
                </Box>
            ) : (
                <List sx={{ p: 0 }}>
                    {activities.map((item) => (
                        <ListItem
                            key={item.id}
                            alignItems="flex-start"
                            sx={{
                                px: 0,
                                py: 1.5,
                                borderBottom:
                                    "1px solid #F1F5F9",
                            }}
                        >
                            <ListItemText
                                primary={
                                    <Box
                                        sx={{
                                            display:
                                                "flex",
                                            alignItems:
                                                "center",
                                            gap: 1,
                                            flexWrap:
                                                "wrap",
                                        }}
                                    >
                                        <Typography
                                            component="span"
                                            fontWeight={
                                                600
                                            }
                                        >
                                            {
                                                item.action
                                            }
                                        </Typography>

                                        <Chip
                                            label={
                                                item.lead_name
                                            }
                                            size="small"
                                            variant="outlined"
                                        />
                                    </Box>
                                }
                                secondary={
                                    <>
                                        <Typography
                                            component="span"
                                            variant="body2"
                                            color="text.secondary"
                                            display="block"
                                        >
                                            {
                                                item.description
                                            }
                                        </Typography>

                                        <Typography
                                            component="span"
                                            variant="caption"
                                            color="text.secondary"
                                        >
                                            {formatWhen(
                                                item.created_at
                                            )}
                                            {item.performed_by
                                                ? ` · ${item.performed_by}`
                                                : ""}
                                        </Typography>
                                    </>
                                }
                            />
                        </ListItem>
                    ))}
                </List>
            )}
        </Paper>
    );
}

export default RecentActivities;
