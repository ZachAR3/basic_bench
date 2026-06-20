export type InventoryItem = {
  id: string;
  name: string;
  quantity: number;
  revision: number;
};

export type InventorySnapshot = Readonly<{
  items: readonly Readonly<InventoryItem>[];
  pending: number;
}>;

type Pending = {
  id: string;
  before: InventoryItem;
};

const clone = (item: InventoryItem): InventoryItem => ({ ...item });

export function createInventoryStore(initial: InventoryItem[]) {
  const items = new Map(initial.map((item) => [item.id, clone(item)]));
  const pending = new Map<string, Pending>();
  const latestByItem = new Map<string, string>();
  const listeners = new Set<() => void>();
  let snapshot: InventorySnapshot | undefined;

  const emit = () => {
    snapshot = undefined;
    listeners.forEach((listener) => listener());
  };
  const setItem = (item: InventoryItem) => items.set(item.id, clone(item));

  return {
    subscribe(listener: () => void) {
      listeners.add(listener);
      return () => listeners.delete(listener);
    },
    getSnapshot(): InventorySnapshot {
      if (!snapshot) {
        const values = [...items.values()]
          .map((item) => Object.freeze(clone(item)))
          .sort((a, b) => a.id.localeCompare(b.id));
        snapshot = Object.freeze({
          items: Object.freeze(values),
          pending: pending.size,
        });
      }
      return snapshot;
    },
    replaceFromServer(next: InventoryItem[]) {
      let changed = false;
      for (const incoming of next) {
        if (latestByItem.has(incoming.id)) continue;
        const current = items.get(incoming.id);
        if (!current || incoming.revision > current.revision) {
          setItem(incoming);
          changed = true;
        }
      }
      if (changed) emit();
    },
    optimisticUpdate(
      requestId: string,
      id: string,
      patch: Partial<Pick<InventoryItem, "name" | "quantity">>,
    ) {
      if (pending.has(requestId)) throw new Error("duplicate request");
      const current = items.get(id);
      if (!current) throw new Error("unknown item");
      pending.set(requestId, { id, before: clone(current) });
      latestByItem.set(id, requestId);
      setItem({ ...current, ...patch });
      emit();
    },
    resolve(requestId: string, serverItem: InventoryItem) {
      const operation = pending.get(requestId);
      if (!operation) return;
      pending.delete(requestId);
      if (latestByItem.get(operation.id) === requestId) {
        latestByItem.delete(operation.id);
        setItem(serverItem);
      }
      emit();
    },
    reject(requestId: string) {
      const operation = pending.get(requestId);
      if (!operation) return;
      pending.delete(requestId);
      if (latestByItem.get(operation.id) === requestId) {
        latestByItem.delete(operation.id);
        setItem(operation.before);
      }
      emit();
    },
  };
}
