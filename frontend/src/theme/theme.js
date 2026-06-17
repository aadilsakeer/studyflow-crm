import { createTheme } from "@mui/material/styles";

const theme = createTheme({
    palette: {
        primary: {
            main: "#2563EB",
        },
        secondary: {
            main: "#7C3AED",
        },
        success: {
            main: "#10B981",
        },
        error: {
            main: "#EF4444",
        },
        background: {
            default: "#F8FAFC",
        },
    },

    typography: {
        fontFamily:
            "'Inter', 'Roboto', sans-serif",

        h4: {
            fontWeight: 700,
        },

        h5: {
            fontWeight: 600,
        },

        h6: {
            fontWeight: 600,
        },
    },

    shape: {
        borderRadius: 12,
    },
});

export default theme;