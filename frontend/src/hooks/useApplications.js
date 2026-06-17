import { useEffect, useState, useCallback } from "react";
import { getApplications } from "../services/applications";

function useApplications(filters = {}) {
    const [applications, setApplications] =
        useState([]);
    const [count, setCount] = useState(0);
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

                if (filters.page) {
                    params.page =
                        filters.page;
                }

                const data =
                    await getApplications(
                        params
                    );

                if (data.results) {
                    setApplications(
                        data.results
                    );
                    setCount(data.count);
                } else {
                    setApplications(
                        Array.isArray(data)
                            ? data
                            : []
                    );
                    setCount(
                        Array.isArray(data)
                            ? data.length
                            : 0
                    );
                }
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
            filters.page,
        ]
    );

    useEffect(() => {
        loadApplications();
    }, [loadApplications]);

    return {
        applications,
        count,
        loading,
        reload: loadApplications,
    };
}

export default useApplications;
