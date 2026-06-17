import { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Toaster } from "react-hot-toast";

import MainLayout from "./layouts/MainLayout";
import LoginPage from "./pages/LoginPage";
import { PermissionsProvider } from "./hooks/usePermissions";
import DashboardPage from "./pages/DashboardPage";
import LeadsPage from "./pages/LeadsPage";
import FollowUpsPage from "./pages/FollowUpsPage";
import StudentsPage from "./pages/StudentsPage";
import ApplicationsPage from "./pages/ApplicationsPage";
import UniversitiesPage from "./pages/UniversitiesPage";
import ComingSoonPage from "./pages/ComingSoonPage";

function App() {
    const [token, setToken] = useState(
        () => localStorage.getItem("access")
    );

    useEffect(() => {
        function handleLogout() {
            setToken(null);
        }

        window.addEventListener(
            "auth:logout",
            handleLogout
        );

        return () => {
            window.removeEventListener(
                "auth:logout",
                handleLogout
            );
        };
    }, []);

    function handleLogin() {
        setToken(localStorage.getItem("access"));
    }

    function handleLogout() {
        localStorage.removeItem("access");
        localStorage.removeItem("refresh");
        localStorage.removeItem("username");
        setToken(null);
    }

    if (!token) {
        return (
            <>
                <Toaster position="top-right" />
                <LoginPage onLogin={handleLogin} />
            </>
        );
    }

    return (
        <PermissionsProvider>
            <BrowserRouter>
                <Toaster position="top-right" />
                <Routes>
                <Route
                    path="/"
                    element={
                        <MainLayout
                            onLogout={handleLogout}
                        />
                    }
                >
                    <Route
                        index
                        element={<DashboardPage />}
                    />
                    <Route
                        path="leads"
                        element={<LeadsPage />}
                    />
                    <Route
                        path="follow-ups"
                        element={<FollowUpsPage />}
                    />
                    <Route
                        path="students"
                        element={<StudentsPage />}
                    />
                    <Route
                        path="applications"
                        element={
                            <ApplicationsPage />
                        }
                    />
                    <Route
                        path="universities"
                        element={
                            <UniversitiesPage />
                        }
                    />
                    <Route
                        path="visa-cases"
                        element={
                            <ComingSoonPage
                                title="Visa Cases"
                                description="Visa case management will be added in a later phase."
                            />
                        }
                    />
                </Route>
            </Routes>
        </BrowserRouter>
        </PermissionsProvider>
    );
}

export default App;
