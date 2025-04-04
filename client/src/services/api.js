// src/services/api.js
const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:5000";

const fetchAPI = async (endpoint, method = "GET", body = null) => {
  const url = `${API_BASE}${endpoint}`;
  const options = {
    method,
    mode: "cors",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: body ? JSON.stringify(body) : null,
  };

  try {
    // First try direct request
    const response = await fetch(url, options);

    if (!response.ok) {
      // If 403, try with preflight
      if (response.status === 403) {
        await fetch(url, { ...options, method: "OPTIONS" });
        return await fetch(url, options);
      }
      throw new Error(`HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API ${method} ${endpoint} failed:`, error);
    throw new Error(`Network error: ${error.message}`);
  }
};

// Public API Methods
export const fetchData = () => fetchAPI("/api/data");

export const generateWordcloud = (spotifyToken) =>
  fetchAPI("/generate_wordcloud", "POST", { token: spotifyToken });
