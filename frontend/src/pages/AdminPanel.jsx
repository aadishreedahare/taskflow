import { useEffect, useState } from "react";
import client from "../api/client";

export default function AdminPanel() {
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [boards, setBoards] = useState([]);
  const [error, setError] = useState("");

  const load = () => {
    Promise.all([client.get("/admin/stats"), client.get("/admin/users"), client.get("/admin/boards")])
      .then(([s, u, b]) => {
        setStats(s.data);
        setUsers(u.data);
        setBoards(b.data);
      })
      .catch(() => setError("Could not load admin data"));
  };

  useEffect(load, []);

  const handleDeleteUser = async (id) => {
    if (!confirm("Delete this user and everything they own?")) return;
    try {
      await client.delete(`/admin/users/${id}`);
      load();
    } catch (err) {
      setError(err.response?.data?.detail || "Could not delete user");
    }
  };

  if (error) return <p className="p-8 text-red-600">{error}</p>;
  if (!stats) return <p className="p-8 text-slate-500">Loading admin dashboard...</p>;

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8">
      <h1 className="text-2xl font-bold mb-6">Admin dashboard</h1>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-8">
        <StatCard label="Users" value={stats.total_users} />
        <StatCard label="Boards" value={stats.total_boards} />
        <StatCard label="Lists" value={stats.total_lists} />
        <StatCard label="Cards" value={stats.total_cards} />
      </div>

      <div className="card-surface p-4 mb-8">
        <h2 className="font-semibold mb-3">Cards by priority</h2>
        <div className="flex gap-4 text-sm">
          {Object.entries(stats.cards_by_priority).map(([k, v]) => (
            <span key={k}>
              {k}: <strong>{v}</strong>
            </span>
          ))}
        </div>
      </div>

      <div className="card-surface p-4 mb-8">
        <h2 className="font-semibold mb-3">Users</h2>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-slate-500 border-b">
              <th className="py-1">Username</th>
              <th>Email</th>
              <th>Admin</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id} className="border-b last:border-0">
                <td className="py-1">{u.username}</td>
                <td>{u.email}</td>
                <td>{u.is_admin ? "Yes" : "No"}</td>
                <td>
                  <button className="text-red-500 text-xs" onClick={() => handleDeleteUser(u.id)}>
                    delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card-surface p-4">
        <h2 className="font-semibold mb-3">All boards</h2>
        <ul className="text-sm space-y-1">
          {boards.map((b) => (
            <li key={b.id}>{b.title}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}

function StatCard({ label, value }) {
  return (
    <div className="card-surface p-4 text-center">
      <p className="text-2xl font-bold text-brand-700">{value}</p>
      <p className="text-xs text-slate-500">{label}</p>
    </div>
  );
}
