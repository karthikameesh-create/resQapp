export function formatDisplayLabel(
  value: string | null | undefined
): string {
  if (!value) {
    return "Unknown";
  }

  const normalized = value.trim();

  const aliases: Record<string, string> = {
    low: "Low",
    Low: "Low",
    high: "High",
    High: "High",
    critical: "Critical",
    Critical: "Critical",
    medium: "Medium",
    Medium: "Medium",
    system_test: "System Testing",
    "system test": "System Testing",
  };

  if (aliases[normalized]) {
    return aliases[normalized];
  }

  return normalized
    .replace(/_/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/\b\w/g, (char) =>
      char.toUpperCase()
    );
}