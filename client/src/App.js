import React, { useState, useEffect } from "react";
import Auth from "./components/Auth";
import Results from "./components/Results";
import "./styles.css";
import { fetchData } from "./services/api";
import { HashRouter as Router } from "react-router-dom";

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const [data, setData] = useState(null);

  useEffect(() => {
    fetchData()
      .then((data) => setData(data))
      .catch(console.error);
  }, []);
  // Render your component

  const handleGenerate = async () => {
    setIsProcessing(true);
    setError(null);

    try {
      const response = await fetch("http://localhost:5000/generate_wordcloud", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });

      const data = await response.json();

      if (data.success) {
        setResults(data);
      } else {
        setError(data.error || "Failed to generate word cloud");
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="app">
      <header>
        <h1>Spotify Lyrics Word Cloud</h1>
        <p>Generate a word cloud from your top Spotify tracks</p>
      </header>

      <main>
        {!isAuthenticated ? (
          <Auth onAuthenticated={() => setIsAuthenticated(true)} />
        ) : (
          <div className="generator">
            {error && <div className="error">{error}</div>}

            {!results ? (
              <button onClick={handleGenerate} disabled={isProcessing}>
                {isProcessing ? "Generating..." : "Generate Word Cloud"}
              </button>
            ) : (
              <Results data={results} />
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
