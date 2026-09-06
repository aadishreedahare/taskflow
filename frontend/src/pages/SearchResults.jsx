import { useEffect, useState } from "react";
import { useSearchParams, Link } from "react-router-dom";
import client from "../api/client";

const PRIORITY_STYLES = {
  low: "bg-slate-100 text-slate-600",
  medium: "bg-amber-100 text-amber-700",
  high: "bg-red-100 text-red-700",
};

export default function SearchResults() {
  const [params] = useSearchParams();
  const q = params.get("q") || "";
  const [priority, setPriority] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    client
      .get("/search/cards", { params: { q, priority: priority || undefined } })
      .then((res) => setResults(res.data))
      .finally(() => setLoading(false));
  }, [q, priority]);

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8">
      <h1 className="text-xl font-bold mb-1">Search results for "{q}"</h1>
      <div className="mb-4">
        <label className="text-sm text-slate-500 mr-2">Filter by priority:</label>
        <select className="input inline-block w-auto" value={priority} onChange={(e) => setPriority(e.target.value)}>
          <option value="">All</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
      </div>

      {loading ? (
        <p className="text-slate-500">Searching...</p>
      ) : results.length === 0 ? (
        <p className="text-slate-500">No cards matched.</p>
      ) : (
        <ul className="space-y-2">
          {results.map((c) => (
            <li key={c.id} className="card-surface p-3">
              <div className="flex items-center justify-between">
                <span className="font-medium">{c.title}</span>
                <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${PRIORITY_STYLES[c.priority]}`}>
                  {c.priority}
                </span>
              </div>
              {c.description && <p className="text-sm text-slate-500 mt-1 line-clamp-2">{c.description}</p>}
            </li>
          ))}
        </ul>
      )}

      <Link to="/" className="text-brand-600 underline text-sm mt-6 inline-block">
        Back to boards
      </Link>
    </div>
  );
}
