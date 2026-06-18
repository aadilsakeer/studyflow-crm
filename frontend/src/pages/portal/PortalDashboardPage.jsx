import { useCallback, useEffect, useState } from "react";

import {
    Paper,
    Typography,
    Grid,
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableRow,
    Button,
    Box,
    Chip,
} from "@mui/material";

import ActivityTimeline from "../../components/ActivityTimeline";
import LoadingState from "../../components/LoadingState";
import {
    getPortalProfile,
    getPortalDocuments,
    getPortalApplications,
    getPortalOffers,
    getPortalVisaCases,
    getPortalTimeline,
    uploadPortalDocument,
} from "../../services/portal";
import { showError, showSuccess } from "../../utils/toast";

function PortalDashboardPage() {
    const [loading, setLoading] = useState(true);
    const [profile, setProfile] = useState(null);
    const [documents, setDocuments] = useState([]);
    const [applications, setApplications] = useState([]);
    const [offers, setOffers] = useState([]);
    const [visaCases, setVisaCases] = useState([]);
    const [timeline, setTimeline] = useState([]);

    const load = useCallback(async () => {
        setLoading(true);

        try {
            const [
                profileData,
                documentData,
                applicationData,
                offerData,
                visaData,
                timelineData,
            ] = await Promise.all([
                getPortalProfile(),
                getPortalDocuments(),
                getPortalApplications(),
                getPortalOffers(),
                getPortalVisaCases(),
                getPortalTimeline(),
            ]);

            setProfile(profileData);
            setDocuments(documentData);
            setApplications(applicationData);
            setOffers(offerData);
            setVisaCases(visaData);
            setTimeline(timelineData.events || []);
        } catch {
            showError("Failed to load portal data.");
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        load();
    }, [load]);

    async function handleUpload(documentId, event) {
        const file = event.target.files?.[0];

        if (!file) return;

        try {
            await uploadPortalDocument(documentId, file);
            showSuccess("Document uploaded.");
            load();
        } catch {
            showError("Upload failed.");
        }
    }

    if (loading) {
        return <LoadingState message="Loading portal..." />;
    }

    return (
        <Box>
            <Paper sx={{ p: 3, mb: 3, borderRadius: 4 }}>
                <Typography variant="h5" fontWeight={700}>
                    Welcome, {profile?.student?.student_id}
                </Typography>
                <Typography color="text.secondary">
                    {profile?.student?.destination_country || "—"}
                </Typography>
            </Paper>

            <Grid container spacing={3}>
                <Grid size={{ xs: 12, md: 6 }}>
                    <Paper sx={{ p: 2, borderRadius: 4 }}>
                        <Typography variant="h6" sx={{ mb: 2 }}>
                            Documents
                        </Typography>
                        <Table size="small">
                            <TableHead>
                                <TableRow>
                                    <TableCell>Type</TableCell>
                                    <TableCell>Status</TableCell>
                                    <TableCell>Action</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {documents.map((doc) => (
                                    <TableRow key={doc.id}>
                                        <TableCell>
                                            {doc.document_type_display}
                                        </TableCell>
                                        <TableCell>
                                            <Chip
                                                label={doc.status_display}
                                                size="small"
                                            />
                                        </TableCell>
                                        <TableCell>
                                            {["requested", "rejected"].includes(
                                                doc.status,
                                            ) && (
                                                <Button
                                                    component="label"
                                                    size="small"
                                                >
                                                    Upload
                                                    <input
                                                        hidden
                                                        type="file"
                                                        onChange={(e) =>
                                                            handleUpload(
                                                                doc.id,
                                                                e,
                                                            )
                                                        }
                                                    />
                                                </Button>
                                            )}
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </Paper>
                </Grid>

                <Grid size={{ xs: 12, md: 6 }}>
                    <Paper sx={{ p: 2, borderRadius: 4, mb: 3 }}>
                        <Typography variant="h6" sx={{ mb: 2 }}>
                            Applications
                        </Typography>
                        {applications.map((item) => (
                            <Box key={item.id} sx={{ mb: 1 }}>
                                <Typography fontWeight={600}>
                                    {item.university_name}
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    {item.course_name} · {item.status}
                                </Typography>
                            </Box>
                        ))}
                    </Paper>

                    <Paper sx={{ p: 2, borderRadius: 4, mb: 3 }}>
                        <Typography variant="h6" sx={{ mb: 2 }}>
                            Offers
                        </Typography>
                        {offers.map((item) => (
                            <Box key={item.id} sx={{ mb: 1 }}>
                                <Typography fontWeight={600}>
                                    {item.university}
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    {item.offer_number} · {item.status_display}
                                </Typography>
                            </Box>
                        ))}
                    </Paper>

                    <Paper sx={{ p: 2, borderRadius: 4 }}>
                        <Typography variant="h6" sx={{ mb: 2 }}>
                            Visa Tracking
                        </Typography>
                        {visaCases.map((item) => (
                            <Box key={item.id} sx={{ mb: 1 }}>
                                <Typography fontWeight={600}>
                                    {item.country}
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    {item.status_display}
                                    {item.appointment_date
                                        ? ` · Appt ${item.appointment_date}`
                                        : ""}
                                </Typography>
                            </Box>
                        ))}
                    </Paper>
                </Grid>

                <Grid size={12}>
                    <Paper sx={{ p: 2, borderRadius: 4 }}>
                        <Typography variant="h6" sx={{ mb: 2 }}>
                            Activity Timeline
                        </Typography>
                        <ActivityTimeline events={timeline} />
                    </Paper>
                </Grid>
            </Grid>
        </Box>
    );
}

export default PortalDashboardPage;
