export type Filters = {
  query: string;
  warehouses: string[];
  lowStock: boolean;
};

export function parseFilters(search: string): Filters {
  const params = new URLSearchParams(search);
  return {
    query: params.get("q") ?? "",
    warehouses: (params.get("warehouses") ?? "").split(","),
    lowStock: params.get("lowStock") === "true",
  };
}

export function serializeFilters(filters: Filters): string {
  const params = new URLSearchParams();
  params.set("q", filters.query);
  params.set("warehouses", filters.warehouses.join(","));
  params.set("lowStock", String(filters.lowStock));
  return `?${params}`;
}
