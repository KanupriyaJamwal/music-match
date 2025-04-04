// src/services/api.js
const API_BASE =
  process.env.REACT_APP_API_URL || "https://music-match-2jb5.onrender.com";

// Unified fetch helper with CORS handling
const fetchWithCORS = async (endpoint, method = "GET", body = null) => {
  const url = `${API_BASE}${endpoint}`;
  const headers = {
    "Content-Type": "application/json",
    Accept: "application/json",
  };

  try {
    // 1. First verify preflight
    const preflight = await fetch(url, {
      method: "OPTIONS",
      mode: "cors",
      headers: {
        ...headers,
        "Access-Control-Request-Method": method,
        Origin: window.location.origin,
      },
    });

    if (!preflight.ok) {
      throw new Error(`Preflight failed: ${preflight.status}`);
    }

    // 2. Make actual request
    const response = await fetch(url, {
      method,
      mode: "cors",
      credentials: "include",
      headers,
      body: body ? JSON.stringify(body) : null,
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status} - ${await response.text()}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API Error (${method} ${endpoint}):`, {
      message: error.message,
      stack: error.stack,
    });
    throw error;
  }
};

// Specific API functions
export const fetchData = async () => {
  return fetchWithCORS("/api/data");
};

export const generateWordcloud = async (spotifyToken) => {
  return fetchWithCORS("/generate_wordcloud", "POST", {
    token: spotifyToken,
  });
};
