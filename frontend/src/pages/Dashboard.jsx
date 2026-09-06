import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import client from "../api/client";

export default function Dashboard() {
  const [boards, setBoards] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState("");

  const loadBoards = () => {
    setLoading(true);
    client
      .get("/boards")
      .then((res) => setBoards(res.data))
      .catch(() => setError("Could not load boards"))
      .finally(() => setLoading(false));
  };

  useEffect(loadBoards, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await client.post("/boards", { title, description: description || null });
      setTitle("");
      setDescription("");
      setShowForm(false);
      loadBoards();
    } catch (err) {
      setError(err.response?.data?.detail || "Could not create board");
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Your boards</h1>
        <button className="btn-primary" onClick={() => setShowForm((s) => !s)}>
          + New board
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="card-surface p-4 mb-6 space-y-3">
          <input
            className="input"
            placeholder="Board title"
            required
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
          <textarea
            className="input"
            placeholder="Description (optional)"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
          {error && <p className="text-sm text-red-600">{error}</p>}
          <div className="flex gap-2">
            <button type="submit" className="btn-primary">
              Create
            </button>
            <button type="button" className="btn-secondary" onClick={() => setShowForm(false)}>
              Cancel
            </button>
          </div>
        </form>
      )}

      {loading ? (
        <p className="text-slate-500">Loading...</p>
      ) : boards.length === 0 ? (
        <p className="text-slate-500">No boards yet. Create your first one above.</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {boards.map((b) => (
            <Link
              key={b.id}
              to={`/boards/${b.id}`}
              className="card-surface p-4 hover:shadow-md transition-shadow"
            >
              <h2 className="font-semibold text-slate-800">{b.title}</h2>
              {b.description && (
                <p className="text-sm text-slate-500 mt-1 line-clamp-2">{b.description}</p>
              )}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
