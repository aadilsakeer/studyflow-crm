import { useEffect, useState, useCallback } from "react";
import { getStudents } from "../services/students";

function useStudents(filters = {}) {
    const [students, setStudents] = useState([]);
    const [loading, setLoading] = useState(true);

    const loadStudents = useCallback(async () => {
        setLoading(true);

        try {
            const response = await getStudents(
                filters
            );

            if (response.results) {
                setStudents(response.results);
            } else {
                setStudents(response);
            }
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    }, [filters.search]);

    useEffect(() => {
        loadStudents();
    }, [loadStudents]);

    return {
        students,
        loading,
        reload: loadStudents,
    };
}

export default useStudents;
