import { useSearchParams } from "react-router-dom";

import {
    Paper,
    Typography,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Chip,
    Box,
    Checkbox,
    ToggleButton,
    ToggleButtonGroup,
} from "@mui/material";

import useFollowUps from "../hooks/useFollowUps";
import LoadingState from "../components/LoadingState";

function FollowUpsPage() {
    const [searchParams, setSearchParams] =
        useSearchParams();

    const filter =
        searchParams.get("filter") || "pending";

    const filters = {
        today: {
            date: "today",
            completed: "false",
        },
        pending: {
            completed: "false",
        },
        completed: {
            completed: "true",
        },
        completed_today: {
            date: "completed_today",
        },
    }[filter] || { completed: "false" };

    const {
        followUps,
        loading,
        toggleComplete,
    } = useFollowUps(filters);

    function handleFilterChange(
        _event,
        value
    ) {
        if (value) {
            setSearchParams({ filter: value });
        }
    }

    if (loading) {
        return (
            <LoadingState message="Loading follow ups..." />
        );
    }

    return (
        <Paper
            elevation={0}
            sx={{
                p: 3,
                borderRadius: 4,
                border: "1px solid #E5E7EB",
            }}
        >
            <Box
                sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    mb: 3,
                    flexWrap: "wrap",
                    gap: 2,
                }}
            >
                <Typography
                    variant="h5"
                    fontWeight={700}
                >
                    Follow Ups
                </Typography>

                <ToggleButtonGroup
                    value={filter}
                    exclusive
                    onChange={handleFilterChange}
                    size="small"
                >
                    <ToggleButton value="today">
                        Today
                    </ToggleButton>
                    <ToggleButton value="pending">
                        Pending
                    </ToggleButton>
                    <ToggleButton value="completed_today">
                        Completed Today
                    </ToggleButton>
                    <ToggleButton value="completed">
                        All Completed
                    </ToggleButton>
                </ToggleButtonGroup>
            </Box>

            <TableContainer>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell>
                                Done
                            </TableCell>
                            <TableCell>
                                Lead
                            </TableCell>
                            <TableCell>
                                Date
                            </TableCell>
                            <TableCell>
                                Notes
                            </TableCell>
                            <TableCell>
                                Status
                            </TableCell>
                        </TableRow>
                    </TableHead>

                    <TableBody>
                        {followUps.length === 0 ? (
                            <TableRow>
                                <TableCell
                                    colSpan={5}
                                    align="center"
                                >
                                    No follow ups
                                    found
                                </TableCell>
                            </TableRow>
                        ) : (
                            followUps.map(
                                (item) => (
                                    <TableRow
                                        key={
                                            item.id
                                        }
                                        hover
                                    >
                                        <TableCell>
                                            <Checkbox
                                                checked={
                                                    item.completed
                                                }
                                                onChange={() =>
                                                    toggleComplete(
                                                        item
                                                    )
                                                }
                                            />
                                        </TableCell>

                                        <TableCell>
                                            {
                                                item.lead_name
                                            }
                                        </TableCell>

                                        <TableCell>
                                            {new Date(
                                                item.follow_up_date
                                            ).toLocaleString()}
                                        </TableCell>

                                        <TableCell>
                                            {item.notes
                                                || "—"}
                                        </TableCell>

                                        <TableCell>
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
                                        </TableCell>
                                    </TableRow>
                                )
                            )
                        )}
                    </TableBody>
                </Table>
            </TableContainer>
        </Paper>
    );
}

export default FollowUpsPage;
