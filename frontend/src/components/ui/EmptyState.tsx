interface EmptyStateProps {
  title: string;
  message: string;
  actionLabel?: string;
  onAction?: () => void;
}

export default function EmptyState({
  title,
  message,
  actionLabel,
  onAction,
}: EmptyStateProps) {
  return (
    <div className="ui-state ui-empty-state">
      <div className="ui-state-icon ui-empty-icon">
        —
      </div>

      <h2>{title}</h2>

      <p>{message}</p>

      {actionLabel && onAction && (
        <button
          type="button"
          className="secondary-button"
          onClick={onAction}
        >
          {actionLabel}
        </button>
      )}
    </div>
  );
}