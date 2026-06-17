import { useEffect, useState, useCallback } from "react";
import { getApplications } from "../services/applications";

function useApplications(filters = {}) {
    const [applications, setApplications] =
        useState([]);
    const [loading, setLoading] =
        useState(true);

    const loadApplications = useCallback(
        async () => {
            setLoading(true);

            try {
                const params = {};

                if (filters.student) {
                    params.student =
                        filters.student;
                }

                if (filters.status) {
                    params.status =
                        filters.status;
                }

                if (filters.search) {
                    params.search =
                        filters.search;
                }

                const data =
                    await getApplications(
                        params
                    );

                setApplications(
                    Array.isArray(data)
                        ? data
                        : data.results
                        || []
                );
            } catch (error) {
                console.error(error);
            } finally {
                setLoading(false);
            }
        },
        [
            filters.student,
            filters.status,
            filters.search,
        ]
    );

    useEffect(() => {
        loadApplications();
    }, [loadApplications]);

    return {
        applications,
        loading,
        reload: loadApplications,
    };
}

export default useApplications;
