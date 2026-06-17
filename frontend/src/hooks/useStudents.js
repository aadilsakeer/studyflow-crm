import { useEffect, useState, useCallback } from "react";
import { getStudents } from "../services/students";

function useStudents(filters = {}) {
    const [students, setStudents] = useState([]);
    const [count, setCount] = useState(0);
    const [loading, setLoading] = useState(true);

    const loadStudents = useCallback(async () => {
        setLoading(true);

        try {
            const params = {};

            if (filters.search) {
                params.search = filters.search;
            }

            if (filters.page) {
                params.page = filters.page;
            }

            const response = await getStudents(params);

            if (response.results) {
                setStudents(response.results);
                setCount(response.count);
            } else {
                setStudents(response);
                setCount(response.length);
            }
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    }, [filters.search, filters.page]);

    useEffect(() => {
        loadStudents();
    }, [loadStudents]);

    return {
        students,
        count,
        loading,
        reload: loadStudents,
    };
}

export default useStudents;
