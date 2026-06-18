import { useCallback, useEffect, useState } from "react";

import { getTasks, updateTask } from "../services/tasks";
import { showError } from "../utils/toast";

function useTasks(filters = {}) {
    const [tasks, setTasks] = useState([]);
    const [count, setCount] = useState(0);
    const [loading, setLoading] = useState(true);

    const loadTasks = useCallback(async () => {
        setLoading(true);

        try {
            const data = await getTasks(filters);

            if (Array.isArray(data.results)) {
                setTasks(data.results);
                setCount(data.count ?? data.results.length);
            } else if (Array.isArray(data)) {
                setTasks(data);
                setCount(data.length);
            } else {
                setTasks([]);
                setCount(0);
            }
        } catch {
            showError("Failed to load tasks.");
        } finally {
            setLoading(false);
        }
    }, [JSON.stringify(filters)]);

    useEffect(() => {
        loadTasks();
    }, [loadTasks]);

    async function saveTaskStatus(task, status) {
        await updateTask(task.id, { status });
        loadTasks();
    }

    return {
        tasks,
        count,
        loading,
        reload: loadTasks,
        saveTaskStatus,
    };
}

export default useTasks;
