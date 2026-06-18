import { useEffect, useState } from "react";
import { Routes, Route, Navigate, useNavigate } from "react-router-dom";

import {
    AppBar,
    Toolbar,
    Typography,
    Button,
    Container,
    Box,
} from "@mui/material";

import PortalDashboardPage from "../pages/portal/PortalDashboardPage";

function PortalLayout() {
    const navigate = useNavigate();
    const token = localStorage.getItem("portal_token");

    useEffect(() => {
        if (!token) {
            navigate("/portal/login");
        }
    }, [token, navigate]);

    function logout() {
        localStorage.removeItem("portal_token");
        localStorage.removeItem("portal_student_id");
        navigate("/portal/login");
    }

    if (!token) {
        return null;
    }

    return (
        <Box>
            <AppBar position="static" color="default" elevation={0}>
                <Toolbar>
                    <Typography variant="h6" sx={{ flexGrow: 1 }}>
                        Student Portal
                    </Typography>
                    <Button onClick={logout}>Logout</Button>
                </Toolbar>
            </AppBar>

            <Container sx={{ py: 3 }}>
                <Routes>
                    <Route
                        index
                        element={<PortalDashboardPage />}
                    />
                    <Route
                        path="dashboard"
                        element={<PortalDashboardPage />}
                    />
                    <Route
                        path="*"
                        element={<Navigate to="/portal/dashboard" />}
                    />
                </Routes>
            </Container>
        </Box>
    );
}

export default PortalLayout;
