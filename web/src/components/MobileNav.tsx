interface MobileNavProps {
  activeRoute: string;
}

export function MobileNav({ activeRoute }: MobileNavProps) {
  const itemClass = (route: string) => `mobile-nav-item ${activeRoute === route ? "active" : ""}`;

  return (
    <nav className="mobile-nav" aria-label="Mobile navigation">
      <a className={itemClass("dashboard")} href="#/"><span>✦</span>Home</a>
      <a className={itemClass("history")} href="#/history"><span>▦</span>Runs</a>
      <a className={itemClass("trace")} href="#/trace"><span>⌁</span>Trace</a>
      <a className={itemClass("settings")} href="#/settings"><span>☰</span>More</a>
    </nav>
  );
}
