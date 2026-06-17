import { useState } from "react";

import useStudents from "../hooks/useStudents";
import StudentDrawer from "../components/StudentDrawer";
import LoadingState from "../components/LoadingState";

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
    TextField,
} from "@mui/material";

function StudentsPage() {
    const [search, setSearch] =
        useState("");

    const [selectedStudent,
        setSelectedStudent] =
        useState(null);

    const [drawerOpen, setDrawerOpen] =
        useState(false);

    const { students, loading, reload } =
        useStudents({ search });

    const filtered = search
        ? students.filter((s) => {
              const term = search.toLowerCase();
              return (
                  s.lead_name
                      ?.toLowerCase()
                      .includes(term)
                  || s.student_id
                      ?.toLowerCase()
                      .includes(term)
                  || s.lead_phone
                      ?.includes(term)
              );
          })
        : students;

    if (loading) {
        return (
            <LoadingState message="Loading students..." />
        );
    }

    return (
        <>
            <StudentDrawer
                open={drawerOpen}
                onClose={() =>
                    setDrawerOpen(false)
                }
                student={selectedStudent}
                onUpdated={reload}
            />

            <Paper
                elevation={0}
                sx={{
                    p: 3,
                    borderRadius: 4,
                    border:
                        "1px solid #E5E7EB",
                }}
            >
                <Box
                    sx={{
                        display: "flex",
                        justifyContent:
                            "space-between",
                        alignItems:
                            "center",
                        mb: 3,
                        gap: 2,
                        flexWrap: "wrap",
                    }}
                >
                    <Typography
                        variant="h5"
                        fontWeight={700}
                    >
                        Students
                    </Typography>

                    <TextField
                        size="small"
                        placeholder="Search students..."
                        value={search}
                        onChange={(e) =>
                            setSearch(
                                e.target.value
                            )
                        }
                        sx={{ width: 280 }}
                    />
                </Box>

                <TableContainer>
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell>
                                    Student ID
                                </TableCell>
                                <TableCell>
                                    Name
                                </TableCell>
                                <TableCell>
                                    Phone
                                </TableCell>
                                <TableCell>
                                    Country
                                </TableCell>
                                <TableCell>
                                    Status
                                </TableCell>
                            </TableRow>
                        </TableHead>

                        <TableBody>
                            {filtered.length
                            === 0 ? (
                                <TableRow>
                                    <TableCell
                                        colSpan={
                                            5
                                        }
                                        align="center"
                                    >
                                        No students
                                        found
                                    </TableCell>
                                </TableRow>
                            ) : (
                                filtered.map(
                                    (
                                        student
                                    ) => (
                                        <TableRow
                                            key={
                                                student.id
                                            }
                                            hover
                                            onClick={() => {
                                                setSelectedStudent(
                                                    student
                                                );
                                                setDrawerOpen(
                                                    true
                                                );
                                            }}
                                            sx={{
                                                cursor:
                                                    "pointer",
                                            }}
                                        >
                                            <TableCell>
                                                {
                                                    student.student_id
                                                }
                                            </TableCell>

                                            <TableCell>
                                                {
                                                    student.lead_name
                                                }
                                            </TableCell>

                                            <TableCell>
                                                {
                                                    student.lead_phone
                                                }
                                            </TableCell>

                                            <TableCell>
                                                {
                                                    student.destination_country
                                                }
                                            </TableCell>

                                            <TableCell>
                                                <Chip
                                                    label={
                                                        student.status
                                                    }
                                                    size="small"
                                                    color="primary"
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
        </>
    );
}

export default StudentsPage;
