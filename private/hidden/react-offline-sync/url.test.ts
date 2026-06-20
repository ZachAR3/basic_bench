import { describe, expect, it } from "vitest";
import { parseFilters, serializeFilters } from "../src/urlState";

describe("URL state", () => {
  it("round-trips repeated Unicode values and preserves unknown fields", () => {
    const parsed = parseFilters(
      "?warehouse=z&x=2&q=%E6%9D%B1%E4%BA%AC&warehouse=a&x=1&lowStock=true",
    );
    expect(parsed).toEqual({
      query: "東京",
      warehouses: ["z", "a"],
      lowStock: true,
      unknown: [["x", "2"], ["x", "1"]],
    });
    expect(serializeFilters(parsed)).toBe(
      "?q=%E6%9D%B1%E4%BA%AC&warehouse=a&warehouse=z&lowStock=true&x=1&x=2",
    );
    expect(serializeFilters(parseFilters(""))).toBe("");
  });
});
