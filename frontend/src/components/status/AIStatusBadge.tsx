interface AIStatusBadgeProps {
  status: string | null | undefined;
}

export default function AIStatusBadge({
  status,
}: AIStatusBadgeProps) {
  const normalized =
    status?.toLowerCase() ?? "unknown";

  return (
    <span
      className={[
        "status-badge",
        "ai-status-badge",
        `ai-${normalized}`,
      ].join(" ")}
    >
      {status || "Unknown"}
    </span>
  );
}