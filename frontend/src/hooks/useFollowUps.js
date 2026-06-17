import { useEffect, useState, useCallback } from "react";
import { getFollowUps, updateFollowUp } from "../services/followups";

function useFollowUps(filters = {}) {
    const [followUps, setFollowUps] = useState([]);
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

            const data = await getFollowUps(params);
            setFollowUps(data);
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    }, [
        filters.completed,
        filters.date,
        filters.lead,
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
        loading,
        reload: loadFollowUps,
        toggleComplete,
    };
}

export default useFollowUps;
