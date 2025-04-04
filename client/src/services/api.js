export const fetchData = async () => {
  const API_URL =
    process.env.REACT_APP_API_URL || "https://music-match-2jb5.onrender.com";

  try {
    // Phase 1: Test OPTIONS preflight directly
    const preflight = await fetch(`${API_URL}/api/data`, {
      method: "OPTIONS",
      mode: "cors",
      headers: {
        "Content-Type": "application/json",
        Origin: "https://kanupriyajamwal.github.io",
      },
    });

    console.log("Preflight status:", preflight.status);

    // Phase 2: Make actual request
    const response = await fetch(`${API_URL}/api/data`, {
      method: "GET",
      mode: "cors",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
    });

    if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error("Full error:", {
      message: error.message,
      stack: error.stack,
    });
    throw error;
  }
};
