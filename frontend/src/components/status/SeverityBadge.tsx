interface SeverityBadgeProps {
  severity: string | null | undefined;
  large?: boolean;
}

export default function SeverityBadge({
  severity,
  large = false,
}: SeverityBadgeProps) {
  const normalized =
    severity?.toLowerCase() ?? "unknown";

  const className = [
    "status-badge",
    "severity-status",
    `severity-${normalized}`,
    large ? "status-badge-large" : "",
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <span className={className}>
      {severity || "Unknown"}
    </span>
  );
}