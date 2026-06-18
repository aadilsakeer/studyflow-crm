import { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Toaster } from "react-hot-toast";

import MainLayout from "./layouts/MainLayout";
import LoginPage from "./pages/LoginPage";
import { PermissionsProvider } from "./hooks/usePermissions";
import { logout as logoutApi } from "./services/auth";
import DashboardPage from "./pages/DashboardPage";
import LeadsPage from "./pages/LeadsPage";
import FollowUpsPage from "./pages/FollowUpsPage";
import TasksPage from "./pages/TasksPage";
import ReportsPage from "./pages/ReportsPage";
import StudentsPage from "./pages/StudentsPage";
import ApplicationsPage from "./pages/ApplicationsPage";
import UniversitiesPage from "./pages/UniversitiesPage";
import StudentDocumentsPage from "./pages/StudentDocumentsPage";
import OfferLettersPage from "./pages/OfferLettersPage";
import VisaCasesPage from "./pages/VisaCasesPage";
import RecycleBinPage from "./pages/RecycleBinPage";
import JourneyBoardPage from "./pages/JourneyBoardPage";
import LeadImportPage from "./pages/LeadImportPage";
import LeadTimelinePage from "./pages/LeadTimelinePage";
import StudentTimelinePage from "./pages/StudentTimelinePage";

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

    async function handleLogout() {
        try {
            await logoutApi();
        } catch (error) {
            console.error("Logout failed:", error);
        }

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
                        path="journey-board"
                        element={<JourneyBoardPage />}
                    />
                    <Route
                        path="leads/:leadId/timeline"
                        element={<LeadTimelinePage />}
                    />
                    <Route
                        path="students/:studentId/timeline"
                        element={<StudentTimelinePage />}
                    />
                    <Route
                        path="leads/import"
                        element={<LeadImportPage />}
                    />
                    <Route
                        path="leads"
                        element={<LeadsPage />}
                    />
                    <Route
                        path="reports"
                        element={<ReportsPage />}
                    />
                    <Route
                        path="tasks"
                        element={<TasksPage />}
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
                        path="student-documents"
                        element={
                            <StudentDocumentsPage />
                        }
                    />
                    <Route
                        path="offer-letters"
                        element={
                            <OfferLettersPage />
                        }
                    />
                    <Route
                        path="visa-cases"
                        element={<VisaCasesPage />}
                    />
                    <Route
                        path="recycle-bin"
                        element={<RecycleBinPage />}
                    />
                </Route>
            </Routes>
        </BrowserRouter>
        </PermissionsProvider>
    );
}

export default App;
