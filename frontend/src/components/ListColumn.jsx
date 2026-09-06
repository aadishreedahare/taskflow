import { useState } from "react";
import { Draggable, Droppable } from "@hello-pangea/dnd";
import CardItem from "./CardItem.jsx";

export default function ListColumn({ list, index, onOpenCard, onAddCard, onRenameList, onDeleteList }) {
  const [adding, setAdding] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [editingTitle, setEditingTitle] = useState(false);
  const [titleDraft, setTitleDraft] = useState(list.title);

  const submitNewCard = async (e) => {
    e.preventDefault();
    if (!newTitle.trim()) return;
    await onAddCard(list.id, newTitle.trim());
    setNewTitle("");
    setAdding(false);
  };

  const submitRename = async () => {
    setEditingTitle(false);
    if (titleDraft.trim() && titleDraft !== list.title) {
      await onRenameList(list.id, titleDraft.trim());
    }
  };

  return (
    <Draggable draggableId={`list-${list.id}`} index={index}>
      {(provided) => (
        <div
          ref={provided.innerRef}
          {...provided.draggableProps}
          className="bg-slate-50 rounded-lg w-72 shrink-0 flex flex-col max-h-full border border-slate-200"
        >
          <div
            {...provided.dragHandleProps}
            className="flex items-center justify-between px-3 py-2 border-b border-slate-200"
          >
            {editingTitle ? (
              <input
                autoFocus
                className="input py-1 text-sm"
                value={titleDraft}
                onChange={(e) => setTitleDraft(e.target.value)}
                onBlur={submitRename}
                onKeyDown={(e) => e.key === "Enter" && submitRename()}
              />
            ) : (
              <h3
                className="font-semibold text-sm text-slate-700 cursor-text"
                onClick={() => setEditingTitle(true)}
              >
                {list.title}{" "}
                <span className="text-slate-400 font-normal">({list.cards.length})</span>
              </h3>
            )}
            <button
              className="text-slate-400 hover:text-red-600 text-xs"
              onClick={() => onDeleteList(list.id)}
              title="Delete list"
            >
              ✕
            </button>
          </div>

          <Droppable droppableId={String(list.id)} type="CARD">
            {(dropProvided, dropSnapshot) => (
              <div
                ref={dropProvided.innerRef}
                {...dropProvided.droppableProps}
                className={`flex-1 overflow-y-auto p-2 min-h-[40px] ${
                  dropSnapshot.isDraggingOver ? "bg-brand-50" : ""
                }`}
              >
                {list.cards.map((card, i) => (
                  <CardItem key={card.id} card={card} index={i} onOpen={onOpenCard} />
                ))}
                {dropProvided.placeholder}
              </div>
            )}
          </Droppable>

          <div className="p-2 border-t border-slate-200">
            {adding ? (
              <form onSubmit={submitNewCard} className="space-y-2">
                <input
                  autoFocus
                  className="input text-sm"
                  placeholder="Card title"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                />
                <div className="flex gap-2">
                  <button type="submit" className="btn-primary text-xs py-1">
                    Add
                  </button>
                  <button
                    type="button"
                    className="btn-secondary text-xs py-1"
                    onClick={() => setAdding(false)}
                  >
                    Cancel
                  </button>
                </div>
              </form>
            ) : (
              <button
                className="text-sm text-slate-500 hover:text-brand-600 w-full text-left"
                onClick={() => setAdding(true)}
              >
                + Add a card
              </button>
            )}
          </div>
        </div>
      )}
    </Draggable>
  );
}
