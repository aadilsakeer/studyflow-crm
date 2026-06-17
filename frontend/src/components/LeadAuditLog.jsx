import {
    Box,
    Typography,
    Chip,
} from "@mui/material";

const FIELD_LABELS = {
    created: "Lead Created",
    first_name: "First Name",
    last_name: "Last Name",
    phone: "Phone",
    email: "Email",
    country_interest: "Country",
    city: "City",
    visa_type: "Visa Type",
    status: "Status",
    remarks: "Remarks",
    budget: "Budget",
    assigned_to: "Assigned To",
    source: "Source",
};

function LeadAuditLog({ items }) {
    if (!items.length) {
        return (
            <Typography
                color="text.secondary"
                sx={{ mt: 1 }}
            >
                No audit records yet
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
                        p: 2,
                        border:
                            "1px solid #E5E7EB",
                        borderRadius: 2,
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
                            {FIELD_LABELS[
                                item.field_changed
                            ]
                                || item.field_changed}
                        </Typography>

                        <Chip
                            label={new Date(
                                item.changed_at
                            ).toLocaleString()}
                            size="small"
                            variant="outlined"
                        />
                    </Box>

                    {item.field_changed
                        !== "created" && (
                        <>
                            <Typography
                                variant="body2"
                                sx={{ mt: 1 }}
                            >
                                <strong>
                                    From:
                                </strong>{" "}
                                {item.old_value
                                    || "—"}
                            </Typography>

                            <Typography
                                variant="body2"
                                sx={{ mt: 0.5 }}
                            >
                                <strong>
                                    To:
                                </strong>{" "}
                                {item.new_value
                                    || "—"}
                            </Typography>
                        </>
                    )}

                    {item.field_changed
                        === "created" && (
                        <Typography
                            variant="body2"
                            color="text.secondary"
                            sx={{ mt: 1 }}
                        >
                            {item.new_value}
                        </Typography>
                    )}

                    {item.changed_by_name && (
                        <Typography
                            variant="caption"
                            color="text.secondary"
                            display="block"
                            sx={{ mt: 0.5 }}
                        >
                            by{" "}
                            {
                                item.changed_by_name
                            }
                        </Typography>
                    )}
                </Box>
            ))}
        </Box>
    );
}

export default LeadAuditLog;
