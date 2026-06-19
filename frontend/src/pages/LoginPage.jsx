import { useState } from "react";
import { Link as RouterLink } from "react-router-dom";

import {
    Box,
    Paper,
    TextField,
    Button,
    Typography,
} from "@mui/material";

import { login } from "../services/auth";
import { useBrand } from "../theme/BrandThemeProvider";
import { showError, showSuccess } from "../utils/toast";

function LoginPage({ onLogin }) {
    const brand = useBrand();
    const [username, setUsername] =
        useState("");

    const [password, setPassword] =
        useState("");

    async function handleLogin() {
        try {
            const data = await login(
                username,
                password
            );

            localStorage.setItem(
                "access",
                data.access
            );

            localStorage.setItem(
                "refresh",
                data.refresh
            );

            localStorage.setItem(
                "username",
                username
            );

            onLogin?.();
            showSuccess("Login successful");
        } catch (error) {
            console.error(error);
            showError("Login failed");
        }
    }

    return (
        <Box
            sx={{
                height: "100vh",
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                backgroundColor: "#F8FAFC",
            }}
        >
            <Paper
                elevation={0}
                sx={{
                    p: 5,
                    width: 420,
                    borderRadius: 4,
                    border: "1px solid #E5E7EB",
                }}
            >
                <Typography
                    variant="h4"
                    fontWeight={700}
                    mb={1}
                >
                    {brand?.brand_name || "Globvio"}
                </Typography>

                <Typography
                    color="text.secondary"
                    mb={4}
                >
                    Sign in to continue
                </Typography>

                <TextField
                    label="Username"
                    fullWidth
                    margin="normal"
                    value={username}
                    onChange={(e) =>
                        setUsername(
                            e.target.value
                        )
                    }
                />

                <TextField
                    label="Password"
                    type="password"
                    fullWidth
                    margin="normal"
                    value={password}
                    onChange={(e) =>
                        setPassword(
                            e.target.value
                        )
                    }
                />

                <Button
                    variant="contained"
                    fullWidth
                    sx={{
                        mt: 3,
                        height: 48,
                    }}
                    onClick={handleLogin}
                >
                    Login
                </Button>
                <Typography variant="body2" sx={{ mt: 2, textAlign: "center" }}>
                    Platform owner?{" "}
                    <RouterLink to="/owner/login-help">Login help</RouterLink>
                </Typography>
            </Paper>
        </Box>
    );
}

export default LoginPage;