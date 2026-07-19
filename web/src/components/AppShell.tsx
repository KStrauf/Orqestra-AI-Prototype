import type { ReactNode } from "react";
import { ContextPanel } from "./ContextPanel";
import { MobileNav } from "./MobileNav";
import { SideNav } from "./SideNav";
import { TopBar } from "./TopBar";
import type { RunSummary } from "../types";

interface AppShellProps {
  children: ReactNode;
  context: ReactNode;
  environmentLabel: string;
  runs: RunSummary[];
  activeRunId: string | null;
  activeRoute: string;
  historyLoading: boolean;
  onSelectRun: (run: RunSummary) => void;
}

export function AppShell({
  children,
  context,
  environmentLabel,
  runs,
  activeRunId,
  activeRoute,
  historyLoading,
  onSelectRun,
}: AppShellProps) {
  return (
    <div className="app-shell">
      <TopBar environmentLabel={environmentLabel} />
      <div className="shell-body">
        <SideNav
          runs={runs}
          activeRunId={activeRunId}
          activeRoute={activeRoute}
          loading={historyLoading}
          onSelectRun={onSelectRun}
        />
        <main className="main-content" id="workspace">{children}</main>
        <ContextPanel>{context}</ContextPanel>
      </div>
      <MobileNav />
    </div>
  );
}
