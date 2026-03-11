export function getDatasetStatusColor(status: string) {
  switch (status) {
    case "PUBLISHED":
      return "bg-blue-200";
    case "INTERNAL_ONLY":
      return "bg-yellow-200";
    case "APPROVED":
      return "bg-green-200";
    case "VALIDATED":
      return "bg-teal-200";
    case "COMPLETED":
      return "bg-violet-200";
    case "DEPRECATED":
      return "bg-gray-200";
    case "DRAFT":
      return "bg-orange-200";
    default:
      return "bg-gray";
  }
}
