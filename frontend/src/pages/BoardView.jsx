import { useEffect, useState, useCallback } from "react";
import { useParams, Link } from "react-router-dom";
import { DragDropContext, Droppable } from "@hello-pangea/dnd";
import client from "../api/client";
import { useAuth } from "../context/AuthContext.jsx";
import ListColumn from "../components/ListColumn.jsx";
import CardModal from "../components/CardModal.jsx";

export default function BoardView() {
  const { boardId } = useParams();
  const { user } = useAuth();
  const [board, setBoard] = useState(null);
  const [error, setError] = useState("");
  const [activeCard, setActiveCard] = useState(null);
  const [newListTitle, setNewListTitle] = useState("");
  const [addingList, setAddingList] = useState(false);
  const [inviteEmail, setInviteEmail] = useState("");
  const [showMembers, setShowMembers] = useState(false);
  const [newLabelName, setNewLabelName] = useState("");
  const [newLabelColor, setNewLabelColor] = useState("#3b82f6");

  const loadBoard = useCallback(() => {
    client
      .get(`/boards/${boardId}`)
      .then((res) => setBoard(res.data))
      .catch(() => setError("Could not load this board (it may not exist, or you may not have access)."));
  }, [boardId]);

  useEffect(loadBoard, [loadBoard]);

  if (error) {
    return (
      <div className="max-w-3xl mx-auto p-8">
        <p className="text-red-600">{error}</p>
        <Link to="/" className="text-brand-600 underline">
          Back to boards
        </Link>
      </div>
    );
  }
  if (!board) return <p className="p-8 text-slate-500">Loading board...</p>;

  const isOwner = board.owner_id === user.id;

  const handleAddList = async (e) => {
    e.preventDefault();
    if (!newListTitle.trim()) return;
    await client.post(`/boards/${boardId}/lists`, { title: newListTitle.trim() });
    setNewListTitle("");
    setAddingList(false);
    loadBoard();
  };

  const handleRenameList = async (listId, title) => {
    await client.patch(`/lists/${listId}`, { title });
    loadBoard();
  };

  const handleDeleteList = async (listId) => {
    if (!confirm("Delete this list and all its cards?")) return;
    await client.delete(`/lists/${listId}`);
    loadBoard();
  };

  const handleAddCard = async (listId, title) => {
    await client.post(`/lists/${listId}/cards`, { title });
    loadBoard();
  };

  const handleInvite = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await client.post(`/boards/${boardId}/members`, { email: inviteEmail });
      setInviteEmail("");
      loadBoard();
    } catch (err) {
      setError(err.response?.data?.detail || "Could not invite that user");
    }
  };

  const handleRemoveMember = async (memberId) => {
    await client.delete(`/boards/${boardId}/members/${memberId}`);
    loadBoard();
  };

  const handleCreateLabel = async (e) => {
    e.preventDefault();
    if (!newLabelName.trim()) return;
    await client.post(`/boards/${boardId}/labels`, { name: newLabelName.trim(), color: newLabelColor });
    setNewLabelName("");
    loadBoard();
  };

  const handleCardUpdated = (updatedCard) => {
    setBoard((prev) => ({
      ...prev,
      lists: prev.lists.map((l) => ({
        ...l,
        cards: l.cards.map((c) => (c.id === updatedCard.id ? { ...c, ...updatedCard } : c)),
      })),
    }));
    setActiveCard((prev) => (prev && prev.id === updatedCard.id ? { ...prev, ...updatedCard } : prev));
  };

  const handleCardDeleted = (cardId) => {
    setBoard((prev) => ({
      ...prev,
      lists: prev.lists.map((l) => ({ ...l, cards: l.cards.filter((c) => c.id !== cardId) })),
    }));
    setActiveCard(null);
  };

  const onDragEnd = async (result) => {
    const { source, destination, type } = result;
    if (!destination) return;
    if (source.droppableId === destination.droppableId && source.index === destination.index) return;

    if (type === "COLUMN") {
      const lists = Array.from(board.lists);
      const [moved] = lists.splice(source.index, 1);
      lists.splice(destination.index, 0, moved);
      setBoard((prev) => ({ ...prev, lists }));
      await Promise.all(lists.map((l, i) => client.patch(`/lists/${l.id}`, { position: i })));
      return;
    }

    // Card drag
    const sourceListId = Number(source.droppableId);
    const destListId = Number(destination.droppableId);
    const lists = board.lists.map((l) => ({ ...l, cards: [...l.cards] }));
    const sourceList = lists.find((l) => l.id === sourceListId);
    const destList = lists.find((l) => l.id === destListId);
    const [moved] = sourceList.cards.splice(source.index, 1);
    destList.cards.splice(destination.index, 0, moved);

    setBoard((prev) => ({ ...prev, lists }));

    const updates = [];
    destList.cards.forEach((c, i) => {
      updates.push(client.patch(`/cards/${c.id}`, { list_id: destListId, position: i }));
    });
    if (sourceListId !== destListId) {
      sourceList.cards.forEach((c, i) => {
        updates.push(client.patch(`/cards/${c.id}`, { position: i }));
      });
    }
    await Promise.all(updates);
  };

  return (
    <div className="h-[calc(100vh-57px)] flex flex-col">
      <div className="px-4 sm:px-6 py-3 flex items-center justify-between border-b border-slate-200 bg-white">
        <div>
          <Link to="/" className="text-xs text-brand-600">
            &larr; All boards
          </Link>
          <h1 className="text-lg font-bold">{board.title}</h1>
        </div>
        <div className="flex items-center gap-2">
          <button className="btn-secondary text-sm" onClick={() => setShowMembers((s) => !s)}>
            Members ({board.members.length + 1})
          </button>
        </div>
      </div>

      {showMembers && (
        <div className="bg-white border-b border-slate-200 px-4 sm:px-6 py-4">
          <h3 className="font-semibold text-sm mb-2">Board members</h3>
          <ul className="text-sm mb-3 space-y-1">
            <li>{board.owner_id === user.id ? user.username : "Owner"} (owner)</li>
            {board.members.map((m) => (
              <li key={m.id} className="flex items-center gap-2">
                {m.username} ({m.email})
                {isOwner && (
                  <button className="text-red-500 text-xs" onClick={() => handleRemoveMember(m.id)}>
                    remove
                  </button>
                )}
              </li>
            ))}
          </ul>
          {isOwner && (
            <form onSubmit={handleInvite} className="flex gap-2 mb-4 max-w-sm">
              <input
                type="email"
                required
                className="input text-sm"
                placeholder="Invite by email"
                value={inviteEmail}
                onChange={(e) => setInviteEmail(e.target.value)}
              />
              <button className="btn-primary text-sm shrink-0">Invite</button>
            </form>
          )}

          <h3 className="font-semibold text-sm mb-2">Labels</h3>
          <div className="flex flex-wrap gap-2 mb-2">
            {board.labels.map((l) => (
              <span
                key={l.id}
                className="px-2 py-1 rounded-full text-xs font-medium text-white"
                style={{ backgroundColor: l.color }}
              >
                {l.name}
              </span>
            ))}
          </div>
          <form onSubmit={handleCreateLabel} className="flex gap-2 max-w-sm">
            <input
              className="input text-sm"
              placeholder="Label name"
              value={newLabelName}
              onChange={(e) => setNewLabelName(e.target.value)}
            />
            <input
              type="color"
              value={newLabelColor}
              onChange={(e) => setNewLabelColor(e.target.value)}
              className="w-10 h-9 border border-slate-300 rounded"
            />
            <button className="btn-secondary text-sm shrink-0">Add label</button>
          </form>
          {error && <p className="text-sm text-red-600 mt-2">{error}</p>}
        </div>
      )}

      <DragDropContext onDragEnd={onDragEnd}>
        <Droppable droppableId="board" type="COLUMN" direction="horizontal">
          {(provided) => (
            <div
              ref={provided.innerRef}
              {...provided.droppableProps}
              className="flex-1 flex gap-3 overflow-x-auto p-4"
            >
              {board.lists.map((list, i) => (
                <ListColumn
                  key={list.id}
                  list={list}
                  index={i}
                  onOpenCard={setActiveCard}
                  onAddCard={handleAddCard}
                  onRenameList={handleRenameList}
                  onDeleteList={handleDeleteList}
                />
              ))}
              {provided.placeholder}

              <div className="w-72 shrink-0">
                {addingList ? (
                  <form onSubmit={handleAddList} className="card-surface p-3 space-y-2">
                    <input
                      autoFocus
                      className="input text-sm"
                      placeholder="List title"
                      value={newListTitle}
                      onChange={(e) => setNewListTitle(e.target.value)}
                    />
                    <div className="flex gap-2">
                      <button className="btn-primary text-xs py-1">Add list</button>
                      <button
                        type="button"
                        className="btn-secondary text-xs py-1"
                        onClick={() => setAddingList(false)}
                      >
                        Cancel
                      </button>
                    </div>
                  </form>
                ) : (
                  <button
                    className="w-full text-left text-sm text-slate-500 hover:text-brand-600 card-surface p-3"
                    onClick={() => setAddingList(true)}
                  >
                    + Add another list
                  </button>
                )}
              </div>
            </div>
          )}
        </Droppable>
      </DragDropContext>

      {activeCard && (
        <CardModal
          card={activeCard}
          boardLabels={board.labels}
          onClose={() => setActiveCard(null)}
          onUpdated={handleCardUpdated}
          onDeleted={handleCardDeleted}
        />
      )}
    </div>
  );
}
