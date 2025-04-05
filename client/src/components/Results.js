import React from "react";
import WordCloud from "./WordCloud";

const Results = ({ data }) => {
  const downloadFile = (filename) => {
    //window.open(
    //  `http://localhost:5000/download/${data.files[filename]}`,
    //  "_blank"
    //);
    // Correct the URL construction

    // <WordCloud imageUrl={data.files["lyrics_wordcloud.png"]} />

    const filePath = data.files[filename].replace("/download/", "");
    window.open(`http://localhost:5001/download/${filePath}`, "_blank");
  };

  return (
    <div className="results">
      <h2>Your Word Cloud is Ready!</h2>
      <div className="output">
        <WordCloud
          imageUrl={`http://localhost:5001/download/${data.files[
            "lyrics_wordcloud.png"
          ].replace("/download/", "")}`}
        />
      </div>

      <div className="downloads">
        <button onClick={() => downloadFile("lyrics_wordcloud.png")}>
          Download Word Cloud
        </button>
        <button onClick={() => downloadFile("top_50_lyrics.txt")}>
          Download Lyrics
        </button>
      </div>

      <div className="console-output">
        <h3>Processing Log:</h3>
        <pre>{data.output}</pre>
      </div>
    </div>
  );
};

export default Results;
