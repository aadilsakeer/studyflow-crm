import { Box, Button, Paper, Typography } from "@mui/material";
import { Link as RouterLink } from "react-router-dom";

export default function OwnerLoginHelpPage() {
    return (
        <Box sx={{ minHeight: "100vh", bgcolor: "#0f172a", color: "#fff", p: 4 }}>
            <Box sx={{ maxWidth: 640, mx: "auto" }}>
                <Typography variant="h4" fontWeight={700} sx={{ mb: 2, color: "#38bdf8" }}>
                    Globvio Owner Login Help
                </Typography>
                <Paper sx={{ p: 3, mb: 2, borderRadius: 3 }}>
                    <Typography variant="h6" gutterBottom>Default owner credentials</Typography>
                    <Typography component="div" sx={{ fontFamily: "monospace", lineHeight: 1.8 }}>
                        Username: owner<br />
                        Email: owner@globvio.local<br />
                        Password: Owner@123
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                        Reset anytime: <code>python manage.py bootstrap_owner</code>
                    </Typography>
                </Paper>
                <Paper sx={{ p: 3, mb: 2, borderRadius: 3 }}>
                    <Typography variant="h6" gutterBottom>How to log in</Typography>
                    <Typography component="ol" sx={{ pl: 2, lineHeight: 1.9 }}>
                        <li>Open the main login page.</li>
                        <li>Sign in with username <strong>owner</strong> and password <strong>Owner@123</strong>.</li>
                        <li>Navigate to <strong>/owner</strong> for the platform owner console.</li>
                    </Typography>
                </Paper>
                <Paper sx={{ p: 3, borderRadius: 3 }}>
                    <Typography variant="body2" color="text.secondary">
                        See <code>docs/onboarding.md</code> for company creation, tenant admins, and password reset.
                    </Typography>
                </Paper>
                <Button component={RouterLink} to="/" sx={{ mt: 3 }} variant="outlined">
                    Back to login
                </Button>
            </Box>
        </Box>
    );
}
