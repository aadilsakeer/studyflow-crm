import DashboardIcon from "@mui/icons-material/Dashboard";
import PeopleIcon from "@mui/icons-material/People";
import SchoolIcon from "@mui/icons-material/School";
import DescriptionIcon from "@mui/icons-material/Description";
import AccountBalanceIcon from "@mui/icons-material/AccountBalance";
import EventIcon from "@mui/icons-material/Event";
import ForumIcon from "@mui/icons-material/Forum";
import TaskAltIcon from "@mui/icons-material/TaskAlt";
import AssessmentIcon from "@mui/icons-material/Assessment";
import FolderIcon from "@mui/icons-material/Folder";
import MailIcon from "@mui/icons-material/Mail";
import FlightTakeoffIcon from "@mui/icons-material/FlightTakeoff";
import DeleteIcon from "@mui/icons-material/Delete";
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

import usePermissions from "../hooks/usePermissions";
import { NAV_PERMISSIONS } from "../utils/permissions";

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
        label: "Reports",
        path: "/reports",
        icon: <AssessmentIcon />,
    },
    {
        label: "Tasks",
        path: "/tasks",
        icon: <TaskAltIcon />,
    },
    {
        label: "Follow Ups",
        path: "/follow-ups",
        icon: <EventIcon />,
    },
    {
        label: "Communications",
        path: "/communications",
        icon: <ForumIcon />,
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
        label: "Documents",
        path: "/student-documents",
        icon: <FolderIcon />,
    },
    {
        label: "Offer Letters",
        path: "/offer-letters",
        icon: <MailIcon />,
    },
    {
        label: "Visa Cases",
        path: "/visa-cases",
        icon: <FlightTakeoffIcon />,
    },
    {
        label: "Recycle Bin",
        path: "/recycle-bin",
        icon: <DeleteIcon />,
        restoreOnly: true,
    },
];

function Sidebar({ onLogout }) {
    const navigate = useNavigate();
    const location = useLocation();
    const { can, canAny } = usePermissions();

    const visibleItems = navItems.filter(
        (item) => {
            if (item.restoreOnly) {
                return canAny([
                    "documents.restore",
                    "offerletters.restore",
                    "visas.restore",
                ]);
            }

            const perm =
                NAV_PERMISSIONS[item.path];

            return !perm || can(perm);
        },
    );

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
                {visibleItems.map((item) => (
                    <ListItemButton
                        key={item.path}
                        selected={
                            location.pathname
                            === item.path
                        }
                        onClick={() =>
                            navigate(item.path)
                        }
                    >
                        <ListItemIcon>
                            {item.icon}
                        </ListItemIcon>
                        <ListItemText
                            primary={item.label}
                        />
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
