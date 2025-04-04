// src/services/api.js
const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:8000";

const fetchAPI = async (endpoint, method = "GET", body = null) => {
  const url = `${API_BASE}${endpoint}`;

  const options = {
    method,
    mode: "cors",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
      Authorization: body?.token ? `Bearer ${body.token}` : undefined,
    },
    body: body ? JSON.stringify(body) : null,
  };

  try {
    // First make OPTIONS preflight request
    const preflight = await fetch(url, {
      method: "OPTIONS",
      headers: {
        Origin: window.location.origin,
        "Access-Control-Request-Method": method,
        "Access-Control-Request-Headers": "Content-Type, Authorization",
      },
    });

    if (!preflight.ok) {
      throw new Error(`Preflight failed: ${preflight.status}`);
    }

    // Then make actual request
    const response = await fetch(url, options);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API ${method} ${endpoint} failed:`, error);
    throw error;
  }
};

// Public API Methods
export const fetchData = () => fetchAPI("/api/data");

export const generateWordcloud = (spotifyToken) =>
  fetchAPI("/generate_wordcloud", "POST", { token: spotifyToken });
