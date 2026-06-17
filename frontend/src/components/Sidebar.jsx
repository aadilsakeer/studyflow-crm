import DashboardIcon from "@mui/icons-material/Dashboard";
import PeopleIcon from "@mui/icons-material/People";
import SchoolIcon from "@mui/icons-material/School";
import DescriptionIcon from "@mui/icons-material/Description";
import AccountBalanceIcon from "@mui/icons-material/AccountBalance";
import FlightTakeoffIcon from "@mui/icons-material/FlightTakeoff";
import EventIcon from "@mui/icons-material/Event";
import LogoutIcon from "@mui/icons-material/Logout";

import {
    Box,
    Typography,
    List,
    ListItemButton,
    ListItemIcon,
    ListItemText,
} from "@mui/material";

import { useLocation, useNavigate } from "react-router-dom";

const navItems = [
    {
        label: "Dashboard",
        path: "/",
        icon: <DashboardIcon />,
    },
    {
        label: "Leads",
        path: "/leads",
        icon: <PeopleIcon />,
    },
    {
        label: "Follow Ups",
        path: "/follow-ups",
        icon: <EventIcon />,
    },
    {
        label: "Students",
        path: "/students",
        icon: <SchoolIcon />,
    },
    {
        label: "Applications",
        path: "/applications",
        icon: <DescriptionIcon />,
    },
    {
        label: "Universities",
        path: "/universities",
        icon: <AccountBalanceIcon />,
    },
    {
        label: "Visa Cases",
        path: "/visa-cases",
        icon: <FlightTakeoffIcon />,
    },
];

function Sidebar({ onLogout }) {
    const navigate = useNavigate();
    const location = useLocation();

    return (
        <Box
            sx={{
                width: 260,
                height: "100vh",
                backgroundColor: "#ffffff",
                borderRight: "1px solid #e5e7eb",
                p: 2,
                display: "flex",
                flexDirection: "column",
            }}
        >
            <Typography
                variant="h5"
                sx={{
                    mb: 4,
                    color: "#2563EB",
                    fontWeight: 700,
                }}
            >
                Globvio
            </Typography>

            <List sx={{ flex: 1 }}>
                {navItems.map((item) => (
                    <ListItemButton
                        key={item.path}
                        selected={location.pathname === item.path}
                        onClick={() => navigate(item.path)}
                    >
                        <ListItemIcon>
                            {item.icon}
                        </ListItemIcon>
                        <ListItemText primary={item.label} />
                    </ListItemButton>
                ))}
            </List>

            <List>
                <ListItemButton onClick={onLogout}>
                    <ListItemIcon>
                        <LogoutIcon />
                    </ListItemIcon>
                    <ListItemText primary="Logout" />
                </ListItemButton>
            </List>
        </Box>
    );
}

export default Sidebar;
