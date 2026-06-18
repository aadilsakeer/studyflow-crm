import { useState } from "react";
import { useNavigate } from "react-router-dom";

import {
    Paper,
    Typography,
    TextField,
    Button,
    Box,
} from "@mui/material";

import { portalLogin } from "../../services/portal";
import { showError } from "../../utils/toast";

function PortalLoginPage() {
    const navigate = useNavigate();
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [loading, setLoading] = useState(false);

    async function handleSubmit(event) {
        event.preventDefault();
        setLoading(true);

        try {
            const data = await portalLogin(username, password);
            localStorage.setItem("portal_token", data.token);
            localStorage.setItem(
                "portal_student_id",
                data.student.student_id,
            );
            navigate("/portal/dashboard");
        } catch {
            showError("Invalid portal credentials.");
        } finally {
            setLoading(false);
        }
    }

    return (
        <Box
            sx={{
                minHeight: "100vh",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                bgcolor: "#F8FAFC",
            }}
        >
            <Paper sx={{ p: 4, width: 400, borderRadius: 4 }}>
                <Typography variant="h5" fontWeight={700} sx={{ mb: 2 }}>
                    Student Portal
                </Typography>

                <form onSubmit={handleSubmit}>
                    <TextField
                        label="Username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        fullWidth
                        sx={{ mb: 2 }}
                        required
                    />
                    <TextField
                        label="Password"
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        fullWidth
                        sx={{ mb: 2 }}
                        required
                    />
                    <Button
                        type="submit"
                        variant="contained"
                        fullWidth
                        disabled={loading}
                    >
                        Sign In
                    </Button>
                </form>
            </Paper>
        </Box>
    );
}

export default PortalLoginPage;
