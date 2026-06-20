import { describe, expect, it } from "vitest";
import { createInventoryStore } from "../src/inventoryStore";

describe("optimistic synchronization", () => {
  it("protects newer edits and rejects stale server data", () => {
    const store = createInventoryStore([
      { id: "a", name: "A", quantity: 1, revision: 5 },
    ]);
    store.optimisticUpdate("old", "a", { quantity: 2 });
    store.optimisticUpdate("new", "a", { quantity: 3 });
    store.resolve("old", { id: "a", name: "A", quantity: 2, revision: 6 });
    expect(store.getSnapshot().items[0].quantity).toBe(3);
    store.replaceFromServer([{ id: "a", name: "server", quantity: 9, revision: 9 }]);
    expect(store.getSnapshot().items[0].quantity).toBe(3);
    store.reject("new");
    expect(store.getSnapshot().items[0].quantity).toBe(2);
    store.replaceFromServer([{ id: "a", name: "old", quantity: 0, revision: 4 }]);
    expect(store.getSnapshot().items[0].quantity).toBe(2);
  });
});
