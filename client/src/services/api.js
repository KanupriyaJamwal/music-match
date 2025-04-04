// src/services/api.js
export const fetchData = async () => {
  try {
    const response = await fetch(`${process.env.REACT_APP_API_URL}/api/data`, {
      method: "GET",
      mode: "cors",
      credentials: "include", // Required if using cookies/auth
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error("API request failed:", error);
    throw error;
  }
};
