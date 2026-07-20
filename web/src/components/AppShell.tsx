import type { ReactNode } from "react";
import { ContextPanel } from "./ContextPanel";
import { MobileNav } from "./MobileNav";
import { SideNav } from "./SideNav";
import { TopBar } from "./TopBar";

interface AppShellProps {
  children: ReactNode;
  context: ReactNode;
  environmentLabel: string;
  activeRunId: string | null;
  activeRoute: string;
  onNewRun: () => void;
}

export function AppShell({
  children,
  context,
  environmentLabel,
  activeRunId,
  activeRoute,
  onNewRun,
}: AppShellProps) {
  return (
    <div className="app-shell">
      <TopBar environmentLabel={environmentLabel} onNewRun={onNewRun} />
      <div className="shell-body">
        <SideNav
          activeRunId={activeRunId}
          activeRoute={activeRoute}
          onNewRun={onNewRun}
        />
        <main className="main-content" id="workspace">{children}</main>
        <ContextPanel>{context}</ContextPanel>
      </div>
      <MobileNav activeRoute={activeRoute} />
    </div>
  );
}
