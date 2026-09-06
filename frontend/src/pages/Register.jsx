import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await register(email, username, password);
      navigate("/");
    } catch (err) {
      setError(err.response?.data?.detail || "Registration failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4">
      <div className="card-surface w-full max-w-sm p-6">
        <h1 className="text-xl font-bold mb-1">Create your account</h1>
        <p className="text-sm text-slate-500 mb-6">
          The first person to register on a fresh install becomes an admin.
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Email</label>
            <input
              type="email"
              required
              className="input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Username</label>
            <input
              required
              minLength={3}
              className="input"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Password</label>
            <input
              type="password"
              required
              minLength={6}
              className="input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <button type="submit" disabled={busy} className="btn-primary w-full">
            {busy ? "Creating account..." : "Register"}
          </button>
        </form>

        <p className="text-sm text-slate-500 mt-4">
          Already have an account?{" "}
          <Link to="/login" className="text-brand-600 font-medium">
            Log in
          </Link>
        </p>
      </div>
    </div>
  );
}
