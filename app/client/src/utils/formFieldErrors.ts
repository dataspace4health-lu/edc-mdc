export function getFieldErrors(
  formErrors: Record<string, string[] | null> | null | undefined,
  fieldName: string,
): string[] | undefined {
  const entries = Object.entries(formErrors ?? {}).filter(([key]) => {
    return key === fieldName || key.startsWith(`${fieldName}.`) || key.startsWith(`${fieldName}[`);
  });

  if (entries.length === 0) return undefined;

  return Array.from(
    new Set(
      entries.flatMap(([, messages]) =>
        Array.isArray(messages) ? messages.filter(Boolean) : messages ? [messages] : [],
      ),
    ),
  );
}
