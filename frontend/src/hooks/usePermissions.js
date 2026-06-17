import {
    createContext,
    useContext,
    useEffect,
    useMemo,
    useState,
} from "react";

import { getCurrentUser } from "../services/auth";
import { createPermissionHelpers } from "../utils/permissions";

const PermissionsContext = createContext(null);

export function PermissionsProvider({ children }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        let active = true;

        async function load() {
            try {
                const data = await getCurrentUser();

                if (active) {
                    setUser(data);
                }
            } catch (error) {
                console.error(
                    "Failed to load permissions:",
                    error,
                );
            } finally {
                if (active) {
                    setLoading(false);
                }
            }
        }

        load();

        return () => {
            active = false;
        };
    }, []);

    const value = useMemo(() => {
        const helpers = createPermissionHelpers(
            user?.permissions || [],
        );

        return {
            user,
            loading,
            ...helpers,
        };
    }, [user, loading]);

    return (
        <PermissionsContext.Provider
            value={value}
        >
            {children}
        </PermissionsContext.Provider>
    );
}

export default function usePermissions() {
    const context = useContext(
        PermissionsContext,
    );

    if (!context) {
        throw new Error(
            "usePermissions must be used within PermissionsProvider"
        );
    }

    return context;
}
