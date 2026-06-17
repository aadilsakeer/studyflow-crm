import { Box, CircularProgress, Typography } from "@mui/material";

function LoadingState({ message = "Loading..." }) {
    return (
        <Box
            sx={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                minHeight: 240,
                gap: 2,
            }}
        >
            <CircularProgress size={32} />
            <Typography color="text.secondary">
                {message}
            </Typography>
        </Box>
    );
}

export default LoadingState;
