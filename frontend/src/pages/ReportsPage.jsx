import { useCallback, useEffect, useState } from "react";

import {
    Paper,
    Typography,
    Box,
    Button,
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableRow,
    Grid,
} from "@mui/material";

import DashboardRangeSelector from "../components/DashboardRangeSelector";
import DashboardChart from "../components/DashboardChart";
import LoadingState from "../components/LoadingState";
import usePermissions from "../hooks/usePermissions";
import {
    getAdvancedReports,
    downloadAdvancedReport,
} from "../services/reports";
import { DEFAULT_DASHBOARD_RANGE } from "../utils/dashboardRanges";
import { showError } from "../utils/toast";

function ReportTable({ title, columns, rows }) {
    return (
        <Paper sx={{ p: 2, borderRadius: 4, mb: 3 }}>
            <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
                {title}
            </Typography>
            <Table size="small">
                <TableHead>
                    <TableRow>
                        {columns.map((col) => (
                            <TableCell key={col.key}>
                                {col.label}
                            </TableCell>
                        ))}
                    </TableRow>
                </TableHead>
                <TableBody>
                    {rows.map((row, index) => (
                        <TableRow key={index}>
                            {columns.map((col) => (
                                <TableCell key={col.key}>
                                    {row[col.key]}
                                </TableCell>
                            ))}
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </Paper>
    );
}

function ReportsPage() {
    const { can } = usePermissions();
    const [range, setRange] = useState(DEFAULT_DASHBOARD_RANGE);
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    const load = useCallback(async () => {
        setLoading(true);

        try {
            const response = await getAdvancedReports(range);
            setData(response);
        } catch {
            showError("Failed to load reports.");
        } finally {
            setLoading(false);
        }
    }, [range]);

    useEffect(() => {
        load();
    }, [load]);

    if (!can("reports.view")) {
        return (
            <Paper sx={{ p: 3 }}>
                <Typography>No access.</Typography>
            </Paper>
        );
    }

    if (loading && !data) {
        return <LoadingState message="Loading reports..." />;
    }

    return (
        <Box>
            <Box
                sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    mb: 2,
                    flexWrap: "wrap",
                    gap: 2,
                }}
            >
                <Box>
                    <Typography variant="h5" fontWeight={700}>
                        Advanced Reports
                    </Typography>
                    <Typography color="text.secondary">
                        {data?.range_label}
                    </Typography>
                </Box>

                <Box sx={{ display: "flex", gap: 1 }}>
                    <Button
                        variant="outlined"
                        onClick={() =>
                            downloadAdvancedReport("csv", range)
                        }
                    >
                        Export CSV
                    </Button>
                    <Button
                        variant="outlined"
                        onClick={() =>
                            downloadAdvancedReport("xlsx", range)
                        }
                    >
                        Export Excel
                    </Button>
                </Box>
            </Box>

            <DashboardRangeSelector
                value={range}
                onChange={setRange}
                label={data?.range_label || "Time Range"}
            />

            <Grid container spacing={3} sx={{ mt: 1, mb: 3 }}>
                <Grid size={{ xs: 12, md: 4 }}>
                    <Paper sx={{ p: 2, borderRadius: 4 }}>
                        <Typography color="text.secondary">
                            Offer Conversion
                        </Typography>
                        <Typography variant="h4" fontWeight={700}>
                            {data?.offer_conversion?.conversion_rate ?? 0}%
                        </Typography>
                    </Paper>
                </Grid>
                <Grid size={{ xs: 12, md: 4 }}>
                    <Paper sx={{ p: 2, borderRadius: 4 }}>
                        <Typography color="text.secondary">
                            Visa Success Rate
                        </Typography>
                        <Typography variant="h4" fontWeight={700}>
                            {data?.visa_success?.success_rate ?? 0}%
                        </Typography>
                    </Paper>
                </Grid>
                <Grid size={{ xs: 12, md: 4 }}>
                    <Paper sx={{ p: 2, borderRadius: 4 }}>
                        <Typography color="text.secondary">
                            Revenue
                        </Typography>
                        <Typography variant="h4" fontWeight={700}>
                            {data?.revenue?.total_revenue ?? 0}
                        </Typography>
                    </Paper>
                </Grid>
            </Grid>

            <Grid container spacing={3} sx={{ mb: 3 }}>
                <Grid size={{ xs: 12, md: 6 }}>
                    <DashboardChart
                        title="Lead Source Volume"
                        subtitle={data?.range_label}
                        trend={data?.charts?.lead_source || []}
                        color="#2563EB"
                    />
                </Grid>
                <Grid size={{ xs: 12, md: 6 }}>
                    <DashboardChart
                        title="Country Performance"
                        subtitle={data?.range_label}
                        trend={data?.charts?.country || []}
                        color="#10B981"
                    />
                </Grid>
                <Grid size={{ xs: 12, md: 6 }}>
                    <DashboardChart
                        title="Telecaller Conversions"
                        subtitle={data?.range_label}
                        trend={data?.charts?.telecaller || []}
                        color="#7C3AED"
                    />
                </Grid>
                <Grid size={{ xs: 12, md: 6 }}>
                    <DashboardChart
                        title="Revenue by Source"
                        subtitle={data?.range_label}
                        trend={data?.charts?.revenue || []}
                        color="#F59E0B"
                    />
                </Grid>
            </Grid>

            <ReportTable
                title="Lead Source ROI"
                columns={[
                    { key: "source", label: "Source" },
                    { key: "leads", label: "Leads" },
                    { key: "converted", label: "Converted" },
                    { key: "conversion_rate", label: "Rate %" },
                    { key: "revenue", label: "Revenue" },
                ]}
                rows={data?.lead_source_roi || []}
            />

            <ReportTable
                title="Telecaller Performance"
                columns={[
                    { key: "name", label: "Telecaller" },
                    { key: "leads", label: "Leads" },
                    { key: "calls", label: "Calls" },
                    { key: "converted", label: "Converted" },
                    { key: "conversion_rate", label: "Rate %" },
                ]}
                rows={data?.telecaller_performance || []}
            />

            <ReportTable
                title="Counsellor Performance"
                columns={[
                    { key: "name", label: "Counsellor" },
                    { key: "leads", label: "Leads" },
                    { key: "converted", label: "Converted" },
                    { key: "conversion_rate", label: "Rate %" },
                ]}
                rows={data?.counsellor_performance || []}
            />

            <ReportTable
                title="University Performance"
                columns={[
                    { key: "university", label: "University" },
                    { key: "applications", label: "Applications" },
                ]}
                rows={data?.university_performance || []}
            />
        </Box>
    );
}

export default ReportsPage;
