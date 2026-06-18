import { useMemo, useState, useEffect } from "react";
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
    Button,
    ToggleButton,
    ToggleButtonGroup,
    IconButton,
} from "@mui/material";

import EditIcon from "@mui/icons-material/Edit";

import useTasks from "../hooks/useTasks";
import LoadingState from "../components/LoadingState";
import TaskFormDialog from "../components/TaskFormDialog";
import usePermissions from "../hooks/usePermissions";
import { getTelecallers, getCounsellors } from "../services/leads";

const FILTER_MAP = {
    due_today: { due_today: "true", status: "pending" },
    pending: { status: "pending" },
    overdue: { overdue: "true" },
    reminder_due: { reminder_due: "true" },
    completed_today: { status: "completed", completed_today: "true" },
    all: {},
};

function TasksPage() {
    const [searchParams, setSearchParams] = useSearchParams();
    const { can } = usePermissions();
    const filter = searchParams.get("filter") || "pending";
    const [dialogOpen, setDialogOpen] = useState(false);
    const [selectedTask, setSelectedTask] = useState(null);
    const [assignees, setAssignees] = useState([]);

    const queryFilters = useMemo(
        () => FILTER_MAP[filter] || FILTER_MAP.pending,
        [filter],
    );

    const {
        tasks,
        loading,
        reload,
        saveTaskStatus,
    } = useTasks(queryFilters);

    useEffect(() => {
        Promise.all([
            getTelecallers(),
            getCounsellors(),
        ]).then(([telecallers, counsellors]) => {
            const merged = [...telecallers, ...counsellors];
            const unique = new Map(
                merged.map((user) => [user.id, user]),
            );
            setAssignees([...unique.values()]);
        }).catch(() => {});
    }, []);

    if (!can("tasks.view")) {
        return (
            <Paper sx={{ p: 3 }}>
                <Typography>No access.</Typography>
            </Paper>
        );
    }

    if (loading) {
        return <LoadingState message="Loading tasks..." />;
    }

    function openCreate() {
        setSelectedTask(null);
        setDialogOpen(true);
    }

    function openEdit(task) {
        setSelectedTask(task);
        setDialogOpen(true);
    }

    return (
        <Paper sx={{ p: 3, borderRadius: 4 }}>
            <Box
                sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    mb: 2,
                }}
            >
                <Typography variant="h5" fontWeight={700}>
                    Tasks
                </Typography>

                {can("tasks.add") && (
                    <Button
                        variant="contained"
                        onClick={openCreate}
                    >
                        New Task
                    </Button>
                )}
            </Box>

            <ToggleButtonGroup
                value={filter}
                exclusive
                onChange={(_e, value) => {
                    if (value) setSearchParams({ filter: value });
                }}
                sx={{ mb: 2 }}
            >
                <ToggleButton value="pending">Pending</ToggleButton>
                <ToggleButton value="due_today">Today</ToggleButton>
                <ToggleButton value="overdue">Overdue</ToggleButton>
                <ToggleButton value="reminder_due">
                    Reminders
                </ToggleButton>
                <ToggleButton value="completed_today">
                    Done Today
                </ToggleButton>
                <ToggleButton value="all">All</ToggleButton>
            </ToggleButtonGroup>

            <TableContainer>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell>Title</TableCell>
                            <TableCell>Type</TableCell>
                            <TableCell>Priority</TableCell>
                            <TableCell>Status</TableCell>
                            <TableCell>Assignee</TableCell>
                            <TableCell>Due</TableCell>
                            <TableCell align="right">Actions</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {tasks.map((task) => (
                            <TableRow key={task.id}>
                                <TableCell>{task.title}</TableCell>
                                <TableCell>
                                    {task.task_type_label}
                                </TableCell>
                                <TableCell>
                                    <Chip
                                        label={task.priority_label}
                                        size="small"
                                    />
                                </TableCell>
                                <TableCell>
                                    <Chip
                                        label={task.status_label}
                                        size="small"
                                        color={
                                            task.status === "completed"
                                                ? "success"
                                                : "default"
                                        }
                                    />
                                </TableCell>
                                <TableCell>
                                    {task.assigned_to_name || "—"}
                                </TableCell>
                                <TableCell>
                                    {task.due_date
                                        ? new Date(
                                            task.due_date,
                                        ).toLocaleString()
                                        : "—"}
                                </TableCell>
                                <TableCell align="right">
                                    {can("tasks.change") && (
                                        <>
                                            <IconButton
                                                size="small"
                                                onClick={() =>
                                                    openEdit(task)
                                                }
                                            >
                                                <EditIcon fontSize="small" />
                                            </IconButton>
                                            {task.status
                                                !== "completed" && (
                                                <Button
                                                    size="small"
                                                    onClick={() =>
                                                        saveTaskStatus(
                                                            task,
                                                            "completed",
                                                        )
                                                    }
                                                >
                                                    Complete
                                                </Button>
                                            )}
                                        </>
                                    )}
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>

            <TaskFormDialog
                open={dialogOpen}
                onClose={() => setDialogOpen(false)}
                task={selectedTask}
                assignees={assignees}
                onSaved={reload}
            />
        </Paper>
    );
}

export default TasksPage;
