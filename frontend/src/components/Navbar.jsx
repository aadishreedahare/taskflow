import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";
import { useAuth } from "../context/AuthContext.jsx";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [q, setQ] = useState("");

  if (!user) return null;

  const handleSearch = (e) => {
    e.preventDefault();
    if (q.trim()) navigate(`/search?q=${encodeURIComponent(q.trim())}`);
  };

  return (
    <nav className="bg-white border-b border-slate-200 px-4 sm:px-6 py-3 flex items-center gap-4">
      <Link to="/" className="font-bold text-lg text-brand-700 shrink-0">
        TaskFlow
      </Link>

      <form onSubmit={handleSearch} className="flex-1 max-w-md">
        <input
          className="input"
          placeholder="Search cards..."
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
      </form>

      <div className="flex items-center gap-3 ml-auto text-sm">
        {user.is_admin && (
          <Link to="/admin" className="text-slate-600 hover:text-brand-700">
            Admin
          </Link>
        )}
        <span className="text-slate-500 hidden sm:inline">{user.username}</span>
        <button className="btn-secondary" onClick={logout}>
          Log out
        </button>
      </div>
    </nav>
  );
}
