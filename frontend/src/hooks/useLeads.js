import { useEffect, useState, useCallback } from "react";
import { getLeads } from "../services/leads";

function useLeads(filters = {}) {
    const [leads, setLeads] = useState([]);
    const [count, setCount] = useState(0);
    const [loading, setLoading] = useState(true);

    const loadLeads = useCallback(async () => {
        setLoading(true);

        try {
            const params = {};

            if (filters.search) {
                params.search = filters.search;
            }

            if (filters.status) {
                params.status = filters.status;
            }

            if (filters.page) {
                params.page = filters.page;
            }

            const response = await getLeads(params);

            if (response.results) {
                setLeads(response.results);
                setCount(response.count);
            } else {
                setLeads(response);
                setCount(response.length);
            }
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    }, [
        filters.search,
        filters.status,
        filters.page,
    ]);

    useEffect(() => {
        loadLeads();
    }, [loadLeads]);

    return {
        leads,
        count,
        loading,
        reload: loadLeads,
    };
}

export default useLeads;
