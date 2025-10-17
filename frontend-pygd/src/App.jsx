import { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage("");

    try {
      // Send POST to your FastAPI backend
      const res = await axios.post(
        "http://localhost:3000/api/v1/user/register",
        { email, password },
        {
          withCredentials: true,
          headers: { "Content-Type": "application/json" },
        }
      );

      // Expecting backend to respond with: { redirect_url: "https://accounts.google.com/o/oauth2/auth..." }
      if (res.data?.redirect_url) {
        setMessage("Redirecting to Google...");
        window.location.href = res.data.redirect_url;
      } else {
        setMessage(
          "Unexpected response:\n" + JSON.stringify(res.data, null, 2)
        );
      }
    } catch (err) {
      console.error("Registration error:", err);
      setMessage("Error: " + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <h1>Register Test</h1>

      <form
        onSubmit={handleRegister}
        style={{
          display: "flex",
          flexDirection: "column",
          width: "250px",
          margin: "auto",
        }}
      >
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          style={{ marginBottom: "10px", padding: "8px" }}
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          style={{ marginBottom: "10px", padding: "8px" }}
        />
        <button type="submit" disabled={loading}>
          {loading ? "Registering..." : "Register"}
        </button>
      </form>

      {message && (
        <pre
          style={{
            background: "#f2f2f2",
            marginTop: "20px",
            padding: "10px",
            textAlign: "left",
            borderRadius: "8px",
            fontSize: "0.9rem",
          }}
        >
          {message}
        </pre>
      )}
    </div>
  );
}

export default App;
