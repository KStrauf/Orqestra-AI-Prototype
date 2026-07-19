export type StudioRouteName = "dashboard" | "new-run" | "run" | "history" | "trace" | "settings";

export interface StudioRoute {
  name: StudioRouteName;
  id?: string;
}

export function routeFromHash(hash: string): StudioRoute {
  const path = hash.replace(/^#/, "") || "/";
  if (path === "/" || path === "/dashboard") return { name: "dashboard" };
  if (path === "/runs/new") return { name: "new-run" };
  if (path === "/history") return { name: "history" };
  if (path === "/settings") return { name: "settings" };
  if (path === "/trace") return { name: "trace" };
  if (path.startsWith("/trace/")) return { name: "trace", id: path.slice(7) };
  if (path.startsWith("/runs/")) return { name: "run", id: path.slice(6) };
  return { name: "dashboard" };
}
