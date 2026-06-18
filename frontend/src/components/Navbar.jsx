import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";

import {
    AppBar,
    Toolbar,
    Typography,
    Avatar,
    Box,
    IconButton,
    Menu,
    MenuItem,
    Divider,
    ListItemIcon,
} from "@mui/material";

import LogoutIcon from "@mui/icons-material/Logout";
import PersonIcon from "@mui/icons-material/Person";

import { getCurrentUser } from "../services/auth";

const PAGE_TITLES = {
    "/": "Dashboard",
    "/leads": "Leads",
    "/follow-ups": "Follow Ups",
    "/tasks": "Tasks",
    "/students": "Students",
    "/applications": "Applications",
    "/universities": "Universities",
    "/student-documents": "Student Documents",
    "/offer-letters": "Offer Letters",
    "/visa-cases": "Visa Cases",
    "/recycle-bin": "Recycle Bin",
    "/leads/import": "Import Leads",
};

function Navbar({ onLogout }) {
    const location = useLocation();

    const [user, setUser] = useState(null);
    const [menuAnchor, setMenuAnchor] =
        useState(null);

    const title =
        PAGE_TITLES[location.pathname]
        || "Globvio CRM";

    useEffect(() => {
        let active = true;

        async function loadUser() {
            try {
                const data = await getCurrentUser();

                if (!active) return;

                setUser(data);

                localStorage.setItem(
                    "username",
                    data.display_name
                    || data.username,
                );
            } catch (error) {
                console.error(
                    "Failed to load user profile:",
                    error,
                );
            }
        }

        loadUser();

        return () => {
            active = false;
        };
    }, []);

    const displayName =
        user?.display_name
        || user?.username
        || localStorage.getItem("username")
        || "User";

    const initial = displayName
        .charAt(0)
        .toUpperCase();

    function handleOpenMenu(event) {
        setMenuAnchor(event.currentTarget);
    }

    function handleCloseMenu() {
        setMenuAnchor(null);
    }

    function handleLogout() {
        handleCloseMenu();
        onLogout?.();
    }

    return (
        <AppBar
            position="static"
            elevation={0}
            sx={{
                backgroundColor: "#fff",
                color: "#000",
                borderBottom:
                    "1px solid #e5e7eb",
            }}
        >
            <Toolbar>
                <Typography
                    variant="h6"
                    sx={{
                        flexGrow: 1,
                        fontWeight: 600,
                    }}
                >
                    {title}
                </Typography>

                <Box
                    sx={{
                        display: "flex",
                        alignItems: "center",
                        gap: 1,
                    }}
                >
                    <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{
                            display: {
                                xs: "none",
                                sm: "block",
                            },
                        }}
                    >
                        {displayName}
                    </Typography>

                    <IconButton
                        onClick={handleOpenMenu}
                        size="small"
                        aria-label="Open profile menu"
                        sx={{ p: 0.5 }}
                    >
                        <Avatar
                            sx={{
                                width: 36,
                                height: 36,
                                bgcolor: "#2563EB",
                                fontSize: 14,
                            }}
                        >
                            {initial}
                        </Avatar>
                    </IconButton>

                    <Menu
                        anchorEl={menuAnchor}
                        open={Boolean(menuAnchor)}
                        onClose={handleCloseMenu}
                        anchorOrigin={{
                            vertical: "bottom",
                            horizontal: "right",
                        }}
                        transformOrigin={{
                            vertical: "top",
                            horizontal: "right",
                        }}
                        slotProps={{
                            paper: {
                                sx: {
                                    mt: 1,
                                    minWidth: 240,
                                    borderRadius: 2,
                                },
                            },
                        }}
                    >
                        <Box sx={{ px: 2, py: 1.5 }}>
                            <Typography
                                fontWeight={600}
                            >
                                {displayName}
                            </Typography>

                            {user?.email && (
                                <Typography
                                    variant="body2"
                                    color="text.secondary"
                                >
                                    {user.email}
                                </Typography>
                            )}

                            {user?.company_name && (
                                <Typography
                                    variant="caption"
                                    color="text.secondary"
                                    display="block"
                                    sx={{ mt: 0.5 }}
                                >
                                    {user.company_name}
                                    {user.role_name
                                        ? ` · ${user.role_name}`
                                        : ""}
                                </Typography>
                            )}
                        </Box>

                        <Divider />

                        <MenuItem disabled>
                            <ListItemIcon>
                                <PersonIcon fontSize="small" />
                            </ListItemIcon>
                            Profile settings
                        </MenuItem>

                        <MenuItem
                            onClick={handleLogout}
                        >
                            <ListItemIcon>
                                <LogoutIcon fontSize="small" />
                            </ListItemIcon>
                            Logout
                        </MenuItem>
                    </Menu>
                </Box>
            </Toolbar>
        </AppBar>
    );
}

export default Navbar;
