import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { InventorySearch } from "./InventorySearch";

const api = async () => [];

createRoot(document.getElementById("root")!).render(
  <StrictMode><InventorySearch api={api} /></StrictMode>,
);
