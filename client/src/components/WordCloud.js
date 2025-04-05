import React from "react";

const WordCloud = ({ imageUrl }) => {
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState(false);

  const handleImageLoad = () => {
    setLoading(false);
  };

  const handleImageError = () => {
    setLoading(false);
    setError(true);
  };

  return (
    <div className="wordcloud">
      {loading && <div className="loading">Loading word cloud...</div>}
      {error && <div className="error">Failed to load word cloud image</div>}
      <img
        src={imageUrl}
        alt="Generated word cloud"
        onLoad={handleImageLoad}
        onError={handleImageError}
        style={{ display: loading ? "none" : "block" }}
      />
    </div>
  );
};

export default WordCloud;
