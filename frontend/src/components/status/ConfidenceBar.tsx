interface ConfidenceBarProps {
  value: number | null | undefined;
  label?: string;
}

export default function ConfidenceBar({
  value,
  label = "Confidence",
}: ConfidenceBarProps) {
  const percentage =
    value === null || value === undefined
      ? null
      : Math.max(
          0,
          Math.min(100, value * 100)
        );

  return (
    <div className="confidence-component">
      <div className="confidence-component-header">
        <span>{label}</span>

        <strong>
          {percentage === null
            ? "Pending"
            : `${percentage.toFixed(1)}%`}
        </strong>
      </div>

      <div className="confidence-component-track">
        <div
          className="confidence-component-fill"
          style={{
            width:
              percentage === null
                ? "0%"
                : `${percentage}%`,
          }}
        />
      </div>
    </div>
  );
}