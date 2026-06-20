export type InventoryItem = {
  id: string;
  name: string;
  quantity: number;
  revision: number;
};

export type InventorySnapshot = Readonly<{
  items: readonly InventoryItem[];
  pending: number;
}>;

type Pending = { id: string; before: InventoryItem };

export function createInventoryStore(initial: InventoryItem[]) {
  const items = initial;
  const pending = new Map<string, Pending>();
  const listeners = new Set<() => void>();

  const emit = () => listeners.forEach((listener) => listener());

  return {
    subscribe(listener: () => void) {
      listeners.add(listener);
      return () => listeners.delete(listener);
    },
    getSnapshot(): InventorySnapshot {
      return { items, pending: pending.size };
    },
    replaceFromServer(next: InventoryItem[]) {
      items.splice(0, items.length, ...next);
      emit();
    },
    optimisticUpdate(
      requestId: string,
      id: string,
      patch: Partial<Pick<InventoryItem, "name" | "quantity">>,
    ) {
      const index = items.findIndex((item) => item.id === id);
      if (index < 0) throw new Error("unknown item");
      pending.set(requestId, { id, before: items[index] });
      Object.assign(items[index], patch);
      emit();
    },
    resolve(requestId: string, serverItem: InventoryItem) {
      const operation = pending.get(requestId);
      if (!operation) return;
      const index = items.findIndex((item) => item.id === operation.id);
      items[index] = serverItem;
      pending.delete(requestId);
      emit();
    },
    reject(requestId: string) {
      const operation = pending.get(requestId);
      if (!operation) return;
      const index = items.findIndex((item) => item.id === operation.id);
      items[index] = operation.before;
      pending.delete(requestId);
      emit();
    },
  };
}
