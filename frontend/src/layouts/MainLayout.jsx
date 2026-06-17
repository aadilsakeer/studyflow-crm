import { Box } from "@mui/material";
import { Outlet } from "react-router-dom";

import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";

function MainLayout({ onLogout }) {
    return (
        <Box sx={{ display: "flex" }}>
            <Sidebar onLogout={onLogout} />

            <Box
                sx={{
                    flex: 1,
                    backgroundColor: "#F8FAFC",
                    minHeight: "100vh",
                }}
            >
                <Navbar onLogout={onLogout} />

                <Box sx={{ p: 4 }}>
                    <Outlet />
                </Box>
            </Box>
        </Box>
    );
}

export default MainLayout;