interface LoadingStateProps {
  message?: string;
  compact?: boolean;
}

export default function LoadingState({
  message = "Loading...",
  compact = false,
}: LoadingStateProps) {
  return (
    <div
      className={[
        "ui-state",
        compact ? "ui-state-compact" : "",
      ]
        .filter(Boolean)
        .join(" ")}
    >
      <div className="ui-spinner" />
      <p>{message}</p>
    </div>
  );
}