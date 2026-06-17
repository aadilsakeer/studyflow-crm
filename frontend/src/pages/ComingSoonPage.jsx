import { Box, Paper, Typography, Button } from "@mui/material";
import { useNavigate } from "react-router-dom";
import ConstructionIcon from "@mui/icons-material/Construction";

function ComingSoonPage({ title, description }) {
    const navigate = useNavigate();

    return (
        <Paper
            elevation={0}
            sx={{
                p: 5,
                borderRadius: 4,
                border: "1px solid #E5E7EB",
                textAlign: "center",
            }}
        >
            <ConstructionIcon
                sx={{
                    fontSize: 56,
                    color: "#2563EB",
                    mb: 2,
                }}
            />

            <Typography
                variant="h5"
                fontWeight={700}
                gutterBottom
            >
                {title}
            </Typography>

            <Typography
                color="text.secondary"
                sx={{ maxWidth: 520, mx: "auto", mb: 3 }}
            >
                {description}
            </Typography>

            <Button
                variant="contained"
                onClick={() => navigate("/")}
            >
                Back to Dashboard
            </Button>
        </Paper>
    );
}

export default ComingSoonPage;
