import { useCallback } from "react";

export function useToggleExpanded(
  setExpandedItems: React.Dispatch<React.SetStateAction<Set<string>>>,
  expandedItems: Set<string>,
) {
  return useCallback(
    (id: string) => {
      const newExpanded = new Set(expandedItems);
      if (newExpanded.has(id)) {
        newExpanded.delete(id);
      } else {
        newExpanded.add(id);
      }
      setExpandedItems(newExpanded);
    },
    [setExpandedItems, expandedItems],
  );
}

export function useToggleSection(
  setExpandedSections: React.Dispatch<Set<string>>,
  expandedSections: Set<string>,
) {
  return useCallback(
    (section: string) => {
      const newExpanded = new Set(expandedSections);
      if (newExpanded.has(section)) {
        newExpanded.delete(section);
      } else {
        newExpanded.add(section);
      }
      setExpandedSections(newExpanded);
    },
    [setExpandedSections, expandedSections],
  );
}
