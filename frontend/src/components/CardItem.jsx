import { Draggable } from "@hello-pangea/dnd";
import { format } from "date-fns";

const PRIORITY_STYLES = {
  low: "bg-slate-100 text-slate-600",
  medium: "bg-amber-100 text-amber-700",
  high: "bg-red-100 text-red-700",
};

export default function CardItem({ card, index, onOpen }) {
  return (
    <Draggable draggableId={String(card.id)} index={index}>
      {(provided, snapshot) => (
        <div
          ref={provided.innerRef}
          {...provided.draggableProps}
          {...provided.dragHandleProps}
          onClick={() => onOpen(card)}
          className={`card-surface p-3 mb-2 cursor-pointer text-sm ${
            snapshot.isDragging ? "shadow-lg ring-2 ring-brand-400" : ""
          }`}
        >
          {card.labels?.length > 0 && (
            <div className="flex flex-wrap gap-1 mb-2">
              {card.labels.map((l) => (
                <span
                  key={l.id}
                  className="px-2 py-0.5 rounded-full text-[10px] font-medium text-white"
                  style={{ backgroundColor: l.color }}
                >
                  {l.name}
                </span>
              ))}
            </div>
          )}

          <p className="font-medium text-slate-800">{card.title}</p>

          <div className="flex items-center gap-2 mt-2 text-xs text-slate-500">
            <span className={`px-2 py-0.5 rounded-full font-medium ${PRIORITY_STYLES[card.priority]}`}>
              {card.priority}
            </span>
            {card.due_date && <span>Due {format(new Date(card.due_date), "MMM d")}</span>}
            {card.comment_count > 0 && <span>💬 {card.comment_count}</span>}
            {card.attachment_count > 0 && <span>📎 {card.attachment_count}</span>}
          </div>
        </div>
      )}
    </Draggable>
  );
}
