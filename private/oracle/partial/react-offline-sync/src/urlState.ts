export type Filters = {
  query: string;
  warehouses: string[];
  lowStock: boolean;
  unknown?: [string, string][];
};

const known = new Set(["q", "warehouse", "lowStock"]);

export function parseFilters(search: string): Filters {
  const params = new URLSearchParams(search);
  return {
    query: params.get("q") ?? "",
    warehouses: params.getAll("warehouse"),
    lowStock: params.get("lowStock") === "true",
    unknown: [...params.entries()].filter(([key]) => !known.has(key)),
  };
}

export function serializeFilters(filters: Filters): string {
  const entries: [string, string][] = [];
  if (filters.query) entries.push(["q", filters.query]);
  for (const warehouse of [...filters.warehouses].sort()) {
    entries.push(["warehouse", warehouse]);
  }
  if (filters.lowStock) entries.push(["lowStock", "true"]);
  entries.push(...(filters.unknown ?? []));
  const params = new URLSearchParams(entries);
  const encoded = params.toString();
  return encoded ? `?${encoded}` : "";
}
