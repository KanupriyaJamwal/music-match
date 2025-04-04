// src/services/api.js
export const fetchData = async () => {
  if (!process.env.REACT_APP_API_URL) {
    throw new Error("API URL is not configured");
  }

  try {
    const response = await fetch(`${process.env.REACT_APP_API_URL}/api/data`);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error("API fetch failed:", error.message);
    throw error;
  }
};
