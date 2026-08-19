interface ErrorStateProps {
  title?: string;
  message: string;
  onRetry?: () => void;
}

export default function ErrorState({
  title = "Something went wrong",
  message,
  onRetry,
}: ErrorStateProps) {
  return (
    <div className="ui-state ui-error-state">
      <div className="ui-state-icon ui-error-icon">
        !
      </div>

      <h2>{title}</h2>

      <p>{message}</p>

      {onRetry && (
        <button
          type="button"
          className="primary-button"
          onClick={onRetry}
        >
          Try Again
        </button>
      )}
    </div>
  );
}