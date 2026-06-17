import { useEffect, useState, useCallback } from "react";
import { getFollowUps, updateFollowUp } from "../services/followups";

function useFollowUps(filters = {}) {
    const [followUps, setFollowUps] = useState([]);
    const [count, setCount] = useState(0);
    const [loading, setLoading] = useState(true);

    const loadFollowUps = useCallback(async () => {
        setLoading(true);

        try {
            const params = {};

            if (filters.completed !== undefined) {
                params.completed = filters.completed;
            }

            if (filters.date) {
                params.date = filters.date;
            }

            if (filters.lead) {
                params.lead = filters.lead;
            }

            if (filters.page) {
                params.page = filters.page;
            }

            const data = await getFollowUps(params);

            if (data.results) {
                setFollowUps(data.results);
                setCount(data.count);
            } else {
                setFollowUps(data);
                setCount(data.length);
            }
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    }, [
        filters.completed,
        filters.date,
        filters.lead,
        filters.page,
    ]);

    useEffect(() => {
        loadFollowUps();
    }, [loadFollowUps]);

    async function toggleComplete(followUp) {
        await updateFollowUp(followUp.id, {
            completed: !followUp.completed,
        });
        loadFollowUps();
    }

    return {
        followUps,
        count,
        loading,
        reload: loadFollowUps,
        toggleComplete,
    };
}

export default useFollowUps;
