import { Box, List, ListItemButton, ListItemText, Typography, Divider } from "@mui/material";
import { Outlet, useLocation, useNavigate } from "react-router-dom";

const NAV = [
    { label: "Dashboard", path: "/owner", exact: true },
    { label: "Companies", path: "/owner/companies", prefix: "/owner/companies" },
    { label: "Modules", path: "/owner/modules" },
    { label: "Subscriptions", path: "/owner/subscriptions" },
    { label: "Support", path: "/owner/support" },
    { label: "Revenue", path: "/owner/revenue" },
    { label: "Customer Success", path: "/owner/customer-success", prefix: "/owner/customer-success" },
    { label: "System Health", path: "/owner/system-health" },
    { label: "Audit Logs", path: "/owner/audit-logs" },
    { label: "Settings", path: "/owner/settings" },
];

function isActive(location, item) {
    if (item.exact) return location.pathname === item.path;
    if (item.prefix) return location.pathname.startsWith(item.prefix);
    return location.pathname === item.path;
}

export default function OwnerLayout({ onLogout }) {
    const navigate = useNavigate();
    const location = useLocation();

    return (
        <Box sx={{ display: "flex", minHeight: "100vh", bgcolor: "#0f172a", color: "#fff" }}>
            <Box
                component="nav"
                sx={{
                    width: 240,
                    flexShrink: 0,
                    p: 2,
                    borderRight: "1px solid #334155",
                    display: "flex",
                    flexDirection: "column",
                }}
            >
                <Typography variant="h6" fontWeight={700} sx={{ mb: 1, color: "#38bdf8" }}>
                    Globvio Owner
                </Typography>
                <Typography variant="caption" sx={{ mb: 2, color: "#94a3b8" }}>
                    Platform console — not tenant CRM
                </Typography>
                <List sx={{ flex: 1 }}>
                    {NAV.map((item) => (
                        <ListItemButton
                            key={item.path}
                            selected={isActive(location, item)}
                            onClick={() => navigate(item.path)}
                            sx={{
                                borderRadius: 2,
                                mb: 0.5,
                                "&.Mui-selected": { bgcolor: "#1e293b", color: "#38bdf8" },
                            }}
                        >
                            <ListItemText primary={item.label} primaryTypographyProps={{ fontSize: 14 }} />
                        </ListItemButton>
                    ))}
                </List>
                <Divider sx={{ borderColor: "#334155", my: 1 }} />
                <ListItemButton onClick={onLogout} sx={{ borderRadius: 2 }}>
                    <ListItemText primary="Logout" />
                </ListItemButton>
            </Box>
            <Box
                component="main"
                sx={{ flex: 1, p: 4, bgcolor: "#f8fafc", color: "#0f172a", minWidth: 0 }}
            >
                <Outlet />
            </Box>
        </Box>
    );
}
