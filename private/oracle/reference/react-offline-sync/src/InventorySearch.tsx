import { useEffect, useRef, useState } from "react";
import type { InventoryItem } from "./inventoryStore";

export type SearchApi = (
  query: string,
  signal: AbortSignal,
) => Promise<InventoryItem[]>;

export function InventorySearch({ api }: { api: SearchApi }) {
  const [query, setQuery] = useState("");
  const [items, setItems] = useState<InventoryItem[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const sequence = useRef(0);

  useEffect(() => {
    const trimmed = query.trim();
    const request = ++sequence.current;
    const controller = new AbortController();
    setError("");
    if (!trimmed) {
      setItems([]);
      setLoading(false);
      return () => controller.abort();
    }
    setLoading(true);
    api(trimmed, controller.signal)
      .then((next) => {
        if (request === sequence.current) setItems(next);
      })
      .catch((reason) => {
        if (
          request === sequence.current
          && !(reason instanceof DOMException && reason.name === "AbortError")
        ) {
          setError(reason instanceof Error ? reason.message : String(reason));
        }
      })
      .finally(() => {
        if (request === sequence.current) setLoading(false);
      });
    return () => controller.abort();
  }, [api, query]);

  return (
    <section aria-busy={loading}>
      <label>
        Search inventory
        <input value={query} onChange={(event) => setQuery(event.target.value)} />
      </label>
      {error && <div role="alert">{error}</div>}
      <ul>{items.map((item) => <li key={item.id}>{item.name}</li>)}</ul>
    </section>
  );
}
