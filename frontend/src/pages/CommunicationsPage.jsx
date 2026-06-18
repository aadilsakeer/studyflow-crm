import { useCallback, useEffect, useState } from "react";

import {
    Paper,
    Typography,
    TextField,
    MenuItem,
    Box,
} from "@mui/material";

import CommunicationHistory from "../components/CommunicationHistory";
import LoadingState from "../components/LoadingState";
import { getCommunicationHistory } from "../services/communications";
import { showError } from "../utils/toast";

function CommunicationsPage() {
    const [loading, setLoading] = useState(true);
    const [events, setEvents] = useState([]);
    const [typeFilter, setTypeFilter] = useState("");

    const load = useCallback(async () => {
        setLoading(true);

        try {
            const params = {};

            if (typeFilter) {
                params.type = typeFilter;
            }

            const data = await getCommunicationHistory(
                params,
            );
            setEvents(data.events || []);
        } catch {
            showError("Failed to load communications.");
        } finally {
            setLoading(false);
        }
    }, [typeFilter]);

    useEffect(() => {
        load();
    }, [load]);

    if (loading) {
        return (
            <LoadingState message="Loading communication hub..." />
        );
    }

    return (
        <Box>
            <Typography variant="h4" fontWeight={700} sx={{ mb: 3 }}>
                Communication Hub
            </Typography>

            <Paper sx={{ p: 2, mb: 3, borderRadius: 4 }}>
                <TextField
                    select
                    label="Filter by type"
                    value={typeFilter}
                    onChange={(e) =>
                        setTypeFilter(e.target.value)
                    }
                    size="small"
                    sx={{ minWidth: 200 }}
                >
                    <MenuItem value="">All</MenuItem>
                    <MenuItem value="call">Calls</MenuItem>
                    <MenuItem value="note">Notes</MenuItem>
                    <MenuItem value="email">Emails</MenuItem>
                    <MenuItem value="whatsapp">
                        WhatsApp
                    </MenuItem>
                </TextField>
            </Paper>

            <CommunicationHistory events={events} />
        </Box>
    );
}

export default CommunicationsPage;
