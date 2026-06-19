import { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Toaster } from "react-hot-toast";

import MainLayout from "./layouts/MainLayout";
import LoginPage from "./pages/LoginPage";
import { PermissionsProvider } from "./hooks/usePermissions";
import usePermissions from "./hooks/usePermissions";
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
import CommunicationsPage from "./pages/CommunicationsPage";
import WhatsAppPage from "./pages/WhatsAppPage";
import PortalLoginPage from "./pages/portal/PortalLoginPage";
import PortalLayout from "./layouts/PortalLayout";
import OnboardingPage from "./pages/OnboardingPage";
import BillingPage from "./pages/BillingPage";
import BrandingPage from "./pages/BrandingPage";
import SupportPage from "./pages/SupportPage";
import SaasAdminPage from "./pages/SaasAdminPage";
import OwnerLayout from "./layouts/OwnerLayout";
import OwnerDashboardPage from "./pages/owner/OwnerDashboardPage";
import OwnerCompaniesPage from "./pages/owner/OwnerCompaniesPage";
import OwnerCompanyDetailPage from "./pages/owner/OwnerCompanyDetailPage";
import { Navigate } from "react-router-dom";

function OwnerRoutes({ onLogout }) {
    return (
        <PermissionsProvider>
            <OwnerGate onLogout={onLogout} />
        </PermissionsProvider>
    );
}

function OwnerGate({ onLogout }) {
    const { user, loading } = usePermissions();
    if (loading) return null;
    if (!user?.is_superuser) return <Navigate to="/" replace />;
    return (
        <Routes>
            <Route path="/" element={<OwnerLayout onLogout={onLogout} />}>
                <Route index element={<OwnerDashboardPage />} />
                <Route path="companies" element={<OwnerCompaniesPage />} />
                <Route path="companies/:id" element={<OwnerCompanyDetailPage />} />
            </Route>
        </Routes>
    );
}

function CrmRoutes({ onLogout }) {
    return (
        <PermissionsProvider>
            <Routes>
                <Route
                    path="/"
                    element={
                        <MainLayout onLogout={onLogout} />
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
                        path="communications"
                        element={<CommunicationsPage />}
                    />
                    <Route
                        path="whatsapp"
                        element={<WhatsAppPage />}
                    />
                    <Route
                        path="students"
                        element={<StudentsPage />}
                    />
                    <Route
                        path="applications"
                        element={<ApplicationsPage />}
                    />
                    <Route
                        path="universities"
                        element={<UniversitiesPage />}
                    />
                    <Route
                        path="student-documents"
                        element={<StudentDocumentsPage />}
                    />
                    <Route
                        path="offer-letters"
                        element={<OfferLettersPage />}
                    />
                    <Route
                        path="visa-cases"
                        element={<VisaCasesPage />}
                    />
                    <Route
                        path="recycle-bin"
                        element={<RecycleBinPage />}
                    />
                    <Route
                        path="billing"
                        element={<BillingPage />}
                    />
                    <Route
                        path="settings/branding"
                        element={<BrandingPage />}
                    />
                    <Route
                        path="support"
                        element={<SupportPage />}
                    />
                    <Route
                        path="saas-admin"
                        element={<SaasAdminPage />}
                    />
                </Route>
            </Routes>
        </PermissionsProvider>
    );
}

function App() {
    const [token, setToken] = useState(
        () => localStorage.getItem("access"),
    );

    useEffect(() => {
        function handleLogout() {
            setToken(null);
        }

        window.addEventListener("auth:logout", handleLogout);

        return () => {
            window.removeEventListener("auth:logout", handleLogout);
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

    return (
        <BrowserRouter>
            <Toaster position="top-right" />
            <Routes>
                <Route
                    path="/portal/login"
                    element={<PortalLoginPage />}
                />
                <Route
                    path="/portal/*"
                    element={<PortalLayout />}
                />
                <Route
                    path="/onboard"
                    element={<OnboardingPage onComplete={handleLogin} />}
                />
                <Route
                    path="/owner/*"
                    element={
                        token ? (
                            <OwnerRoutes onLogout={handleLogout} />
                        ) : (
                            <Navigate to="/" replace />
                        )
                    }
                />
                <Route
                    path="/*"
                    element={
                        token ? (
                            <CrmRoutes onLogout={handleLogout} />
                        ) : (
                            <LoginPage onLogin={handleLogin} />
                        )
                    }
                />
            </Routes>
        </BrowserRouter>
    );
}

export default App;
