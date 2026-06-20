import { describe, expect, it } from "vitest";
import { createInventoryStore } from "../src/inventoryStore";

describe("external-store snapshot", () => {
  it("is stable and immutable until state changes", () => {
    const input = [{ id: "a", name: "A", quantity: 1, revision: 1 }];
    const store = createInventoryStore(input);
    const first = store.getSnapshot();
    expect(store.getSnapshot()).toBe(first);
    expect(() => ((first.items[0] as any).name = "mutated")).toThrow();
    expect(store.getSnapshot().items[0].name).toBe("A");
    store.optimisticUpdate("r1", "a", { quantity: 2 });
    expect(store.getSnapshot()).not.toBe(first);
    expect(input[0].quantity).toBe(1);
  });
});
