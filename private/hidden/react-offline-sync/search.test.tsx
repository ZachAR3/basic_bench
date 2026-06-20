import React from "react";
import { act, fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { InventorySearch, type SearchApi } from "../src/InventorySearch";

const item = (name: string) => [{ id: name, name, quantity: 1, revision: 1 }];

describe("search lifecycle", () => {
  it("ignores stale work, suppresses aborts, and exposes real errors", async () => {
    const resolvers: ((value: ReturnType<typeof item>) => void)[] = [];
    const signals: AbortSignal[] = [];
    const api: SearchApi = (query, signal) => {
      signals.push(signal);
      if (query === "bad") return Promise.reject(new Error("offline"));
      return new Promise((resolve) => resolvers.push(resolve));
    };
    render(<InventorySearch api={api} />);
    expect(signals).toHaveLength(0);
    const input = screen.getByLabelText("Search inventory");
    fireEvent.change(input, { target: { value: "first" } });
    fireEvent.change(input, { target: { value: "second" } });
    expect(signals[0].aborted).toBe(true);
    await act(async () => {
      resolvers[1](item("new"));
      resolvers[0](item("stale"));
    });
    expect(screen.getByText("new")).toBeTruthy();
    expect(screen.queryByText("stale")).toBeNull();
    fireEvent.change(input, { target: { value: "bad" } });
    expect((await screen.findByRole("alert")).textContent).toContain("offline");
  });
});
