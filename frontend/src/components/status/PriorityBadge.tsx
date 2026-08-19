interface PriorityBadgeProps {
  priority: string | null | undefined;
  large?: boolean;
}

export default function PriorityBadge({
  priority,
  large = false,
}: PriorityBadgeProps) {
  const normalized =
    priority?.toLowerCase() ?? "unknown";

  const className = [
    "status-badge",
    "priority-status",
    `priority-${normalized}`,
    large ? "status-badge-large" : "",
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <span className={className}>
      {priority || "Unknown"}
    </span>
  );
}