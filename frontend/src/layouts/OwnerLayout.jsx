import { Box, List, ListItemButton, ListItemText, Typography } from "@mui/material";
import { Outlet, useLocation, useNavigate } from "react-router-dom";

const links = [
    { label: "Dashboard", path: "/owner" },
    { label: "Companies", path: "/owner/companies" },
    { label: "Modules", path: "/owner/modules" },
];

export default function OwnerLayout({ onLogout }) {
    const navigate = useNavigate();
    const location = useLocation();

    return (
        <Box sx={{ display: "flex", minHeight: "100vh", bgcolor: "#0f172a", color: "#fff" }}>
            <Box sx={{ width: 220, p: 2, borderRight: "1px solid #334155" }}>
                <Typography variant="h6" fontWeight={700} sx={{ mb: 3, color: "#38bdf8" }}>
                    Globvio Owner
                </Typography>
                <List>
                    {links.map((l) => (
                        <ListItemButton
                            key={l.path}
                            selected={location.pathname === l.path}
                            onClick={() => navigate(l.path)}
                            sx={{ borderRadius: 2, mb: 0.5 }}
                        >
                            <ListItemText primary={l.label} />
                        </ListItemButton>
                    ))}
                </List>
                <ListItemButton onClick={onLogout} sx={{ mt: 4, borderRadius: 2 }}>
                    <ListItemText primary="Logout" />
                </ListItemButton>
            </Box>
            <Box sx={{ flex: 1, p: 4, bgcolor: "#f8fafc", color: "#0f172a" }}>
                <Outlet />
            </Box>
        </Box>
    );
}
