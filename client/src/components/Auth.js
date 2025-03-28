import React from "react";

const Auth = ({ onAuthenticated }) => {
  const handleLogin = () => {
    // In a real app, you would implement Spotify OAuth here
    // For this demo, we'll just simulate authentication
    onAuthenticated();
  };

  return (
    <div className="auth">
      <p>Please authenticate with Spotify to continue</p>
      <button onClick={handleLogin}>Login with Spotify</button>
    </div>
  );
};

export default Auth;
