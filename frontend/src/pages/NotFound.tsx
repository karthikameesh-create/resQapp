import { useNavigate } from "react-router-dom";

export default function NotFound() {
  const navigate = useNavigate();

  return (
    <div className="ui-state">
      <div className="ui-state-icon ui-empty-icon">
        404
      </div>

      <h2>Page not found</h2>

      <p>
        The page you're looking for doesn't
        exist.
      </p>

      <button
        type="button"
        className="primary-button"
        onClick={() =>
          navigate("/dashboard")
        }
      >
        Back to Dashboard
      </button>
    </div>
  );
}