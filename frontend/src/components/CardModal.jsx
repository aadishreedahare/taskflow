import { useEffect, useState } from "react";
import client from "../api/client";
import { useAuth } from "../context/AuthContext.jsx";

export default function CardModal({ card, boardLabels, onClose, onUpdated, onDeleted }) {
  const { user } = useAuth();
  const [title, setTitle] = useState(card.title);
  const [description, setDescription] = useState(card.description || "");
  const [priority, setPriority] = useState(card.priority);
  const [dueDate, setDueDate] = useState(card.due_date || "");
  const [labels, setLabels] = useState(card.labels || []);
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState("");
  const [attachments, setAttachments] = useState([]);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    client.get(`/cards/${card.id}/comments`).then((res) => setComments(res.data));
    client.get(`/cards/${card.id}/attachments`).then((res) => setAttachments(res.data));
  }, [card.id]);

  const saveField = async (fields) => {
    setSaving(true);
    setError("");
    try {
      const res = await client.patch(`/cards/${card.id}`, fields);
      onUpdated(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Could not save");
    } finally {
      setSaving(false);
    }
  };

  const toggleLabel = async (label) => {
    const has = labels.some((l) => l.id === label.id);
    const res = has
      ? await client.delete(`/cards/${card.id}/labels/${label.id}`)
      : await client.post(`/cards/${card.id}/labels/${label.id}`);
    setLabels(res.data.labels);
    onUpdated(res.data);
  };

  const submitComment = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;
    const res = await client.post(`/cards/${card.id}/comments`, { content: newComment.trim() });
    setComments((c) => [...c, res.data]);
    setNewComment("");
    onUpdated({ ...card, comment_count: comments.length + 1, labels });
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await client.post(`/cards/${card.id}/attachments`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setAttachments((a) => [...a, res.data]);
      onUpdated({ ...card, attachment_count: attachments.length + 1, labels });
    } catch (err) {
      setError(err.response?.data?.detail || "Upload failed");
    }
    e.target.value = "";
  };

  const downloadAttachment = async (att) => {
    const res = await client.get(`/attachments/${att.id}/download`, { responseType: "blob" });
    const url = window.URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement("a");
    link.href = url;
    link.download = att.filename;
    link.click();
    window.URL.revokeObjectURL(url);
  };

  const deleteAttachment = async (att) => {
    await client.delete(`/attachments/${att.id}`);
    setAttachments((a) => a.filter((x) => x.id !== att.id));
  };

  const handleDelete = async () => {
    if (!confirm("Delete this card?")) return;
    await client.delete(`/cards/${card.id}`);
    onDeleted(card.id);
  };

  return (
    <div className="fixed inset-0 bg-black/40 flex items-start justify-center p-4 sm:p-8 overflow-y-auto z-50">
      <div className="card-surface w-full max-w-2xl p-6 my-4">
        <div className="flex justify-between items-start mb-4">
          <input
            className="text-lg font-bold flex-1 border-none focus:outline-none focus:ring-2 focus:ring-brand-500 rounded px-1 -ml-1"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            onBlur={() => title.trim() && title !== card.title && saveField({ title: title.trim() })}
          />
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 text-xl leading-none ml-3">
            ✕
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-xs font-medium text-slate-500 mb-1">Priority</label>
            <select
              className="input"
              value={priority}
              onChange={(e) => {
                setPriority(e.target.value);
                saveField({ priority: e.target.value });
              }}
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-500 mb-1">Due date</label>
            <input
              type="date"
              className="input"
              value={dueDate}
              onChange={(e) => {
                setDueDate(e.target.value);
                saveField({ due_date: e.target.value || null });
              }}
            />
          </div>
        </div>

        <div className="mb-4">
          <label className="block text-xs font-medium text-slate-500 mb-1">Labels</label>
          <div className="flex flex-wrap gap-2">
            {boardLabels.map((l) => {
              const active = labels.some((cl) => cl.id === l.id);
              return (
                <button
                  key={l.id}
                  onClick={() => toggleLabel(l)}
                  className="px-2 py-1 rounded-full text-xs font-medium border"
                  style={{
                    backgroundColor: active ? l.color : "white",
                    borderColor: l.color,
                    color: active ? "white" : l.color,
                  }}
                >
                  {l.name}
                </button>
              );
            })}
            {boardLabels.length === 0 && (
              <p className="text-xs text-slate-400">No labels on this board yet.</p>
            )}
          </div>
        </div>

        <div className="mb-4">
          <label className="block text-xs font-medium text-slate-500 mb-1">Description</label>
          <textarea
            className="input min-h-[80px]"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            onBlur={() => description !== (card.description || "") && saveField({ description })}
          />
        </div>

        <div className="mb-4">
          <label className="block text-xs font-medium text-slate-500 mb-1">Attachments</label>
          <ul className="space-y-1 mb-2">
            {attachments.map((att) => (
              <li key={att.id} className="flex items-center justify-between text-sm bg-slate-50 rounded px-2 py-1">
                <button className="text-brand-600 hover:underline text-left truncate" onClick={() => downloadAttachment(att)}>
                  📎 {att.filename}
                </button>
                <button className="text-slate-400 hover:text-red-600 text-xs ml-2" onClick={() => deleteAttachment(att)}>
                  Remove
                </button>
              </li>
            ))}
          </ul>
          <input type="file" onChange={handleFileUpload} className="text-sm" />
        </div>

        <div className="mb-4">
          <label className="block text-xs font-medium text-slate-500 mb-1">Comments</label>
          <ul className="space-y-2 mb-2 max-h-40 overflow-y-auto">
            {comments.map((c) => (
              <li key={c.id} className="text-sm bg-slate-50 rounded px-2 py-1">
                <span className="font-medium">{c.username || `user #${c.user_id}`}: </span>
                {c.content}
              </li>
            ))}
            {comments.length === 0 && <p className="text-xs text-slate-400">No comments yet.</p>}
          </ul>
          <form onSubmit={submitComment} className="flex gap-2">
            <input
              className="input"
              placeholder={`Comment as ${user?.username}...`}
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
            />
            <button className="btn-primary shrink-0" type="submit">
              Post
            </button>
          </form>
        </div>

        {error && <p className="text-sm text-red-600 mb-2">{error}</p>}

        <div className="flex justify-between items-center pt-2 border-t border-slate-200">
          <span className="text-xs text-slate-400">{saving ? "Saving..." : ""}</span>
          <button className="btn-danger" onClick={handleDelete}>
            Delete card
          </button>
        </div>
      </div>
    </div>
  );
}
