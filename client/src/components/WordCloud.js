import React from "react";

const WordCloud = ({ imageUrl }) => {
  return (
    <div className="wordcloud">
      <img
        //src={`http://localhost:5001${imageUrl}`}
        src={imageUrl}
        alt="Generated word cloud"
      />
    </div>
  );
};

export default WordCloud;
