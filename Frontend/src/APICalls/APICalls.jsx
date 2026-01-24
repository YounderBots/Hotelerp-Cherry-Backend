export const baseURL = "http://127.0.0.1:8000";

const getAuthHeader = () => ({
    Authorization: `Bearer ${localStorage.getItem("AuthToken")}`,
    company_id : 'COMP001'
});

const handleResponse = async (response) => {
    const result = await response.json();
    console.log('Result',result);
    

    if (!response.ok) {
        throw new Error(result.detail || result.message || "API Error");
    }

    return result;
};

const APICall = {
    // -------------------------
    // POST (Without Token)
    // -------------------------
    postWT: async (endpoint, payload = {}) => {
        try {

            const response = await fetch(`${baseURL}${endpoint}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(payload),
            });

            return await handleResponse(response);
        } catch (err) {
            throw new Error(err.message || "POST request failed");
        }
    },

    // -------------------------
    // POST (With Token)
    // -------------------------
    postT: async (endpoint, payload = {}) => {
        try {
            const response = await fetch(`${baseURL}${endpoint}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    ...getAuthHeader(),
                },
                body: JSON.stringify(payload),
            });

            return await handleResponse(response);
        } catch (err) {
            throw new Error(err.message || "POST request failed");
        }
    },

    // -------------------------
    // GET (Without Token)
    // -------------------------
    getWT: async (endpoint, params = {}) => {
        try {
            const query = new URLSearchParams(params).toString();
            const url = query ? `${baseURL}${endpoint}?${query}` : `${baseURL}${endpoint}`;



            const response = await fetch(url, {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                },
            });

            return await handleResponse(response);
        } catch (err) {
            throw new Error(err.message || "GET request failed");
        }
    },

    // -------------------------
    // GET (With Token)
    // -------------------------
    getT: async (endpoint, params = {}) => {
        try {

            const query = new URLSearchParams(params).toString();
            const url = query ? `${baseURL}${endpoint}?${query}` : `${baseURL}${endpoint}`;



            const response = await fetch(url, {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                    ...getAuthHeader(),
                },
            });

            return await handleResponse(response);
        } catch (err) {
            throw new Error(err.message || "GET request failed");
        }
    },

    // -------------------------
    // PUT (With Token)
    // -------------------------
    putT: async (endpoint, payload = {}) => {
        try {
            const response = await fetch(`${baseURL}${endpoint}`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    ...getAuthHeader(),
                },
                body: JSON.stringify(payload),
            });

            return await handleResponse(response);
        } catch (err) {
            throw new Error(err.message || "PUT request failed");
        }
    },

    // -------------------------
    // DELETE (With Token)
    // -------------------------
    deleteT: async (endpoint) => {
        try {
            const response = await fetch(`${baseURL}${endpoint}`, {
                method: "DELETE",
                headers: {
                    "Content-Type": "application/json",
                    ...getAuthHeader(),
                },
            });

            return await handleResponse(response);
        } catch (err) {
            throw new Error(err.message || "DELETE request failed");
        }
    },
};

export default APICall;