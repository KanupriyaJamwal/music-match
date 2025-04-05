import React from "react";
import WordCloud from "./WordCloud";

const Results = ({ data }) => {
  // Use a consistent base URL that works for both development and production
  const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:5001";

  const downloadFile = (filename) => {
    if (!data.files || !data.files[filename]) {
      console.error(`File path for ${filename} not found in response`);
      return;
    }

    const filePath = data.files[filename];
    window.open(`${API_BASE}/download/${filePath}`, "_blank");
  };

  return (
    <div className="results">
      <h2>Your Word Cloud is Ready!</h2>

      {data.files && data.files["lyrics_wordcloud.png"] ? (
        <div className="output">
          <WordCloud
            imageUrl={`${API_BASE}/download/${data.files["lyrics_wordcloud.png"]}`}
          />
        </div>
      ) : (
        <div className="error">Word cloud image not available</div>
      )}

      <div className="downloads">
        {data.files && data.files["lyrics_wordcloud.png"] && (
          <button onClick={() => downloadFile("lyrics_wordcloud.png")}>
            Download Word Cloud
          </button>
        )}

        {data.files && data.files["top_50_lyrics.txt"] && (
          <button onClick={() => downloadFile("top_50_lyrics.txt")}>
            Download Lyrics
          </button>
        )}
      </div>

      {data.output && (
        <div className="console-output">
          <h3>Processing Log:</h3>
          <pre>{data.output}</pre>
        </div>
      )}
    </div>
  );
};

export default Results;
