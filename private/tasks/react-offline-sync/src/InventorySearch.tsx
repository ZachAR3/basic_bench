import { useEffect, useState } from "react";
import type { InventoryItem } from "./inventoryStore";

export type SearchApi = (
  query: string,
  signal: AbortSignal,
) => Promise<InventoryItem[]>;

export function InventorySearch({ api }: { api: SearchApi }) {
  const [query, setQuery] = useState("");
  const [items, setItems] = useState<InventoryItem[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();
    api(query, controller.signal)
      .then(setItems)
      .catch((reason) => setError(String(reason)));
    return () => controller.abort();
  }, [api, query]);

  return (
    <section>
      <label>
        Search inventory
        <input value={query} onChange={(event) => setQuery(event.target.value)} />
      </label>
      {error && <div>{error}</div>}
      <ul>{items.map((item) => <li key={item.id}>{item.name}</li>)}</ul>
    </section>
  );
}
