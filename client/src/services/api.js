// src/services/api.js
export const fetchData = async () => {
  try {
    const response = await fetch(`${process.env.REACT_APP_API_URL}/api/data`);
    if (!response.ok) throw new Error("Network response was not ok");
    return await response.json();
  } catch (error) {
    console.error("Error fetching data:", error);
    throw error;
  }
};
