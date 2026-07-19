export function MobileNav() {
  return (
    <nav className="mobile-nav" aria-label="Mobile navigation">
      <a className="mobile-nav-item active" href="#/"><span>✦</span>Home</a>
      <a className="mobile-nav-item" href="#/history"><span>▦</span>Runs</a>
      <a className="mobile-nav-item" href="#/trace"><span>⌁</span>Trace</a>
      <a className="mobile-nav-item" href="#/settings"><span>☰</span>More</a>
    </nav>
  );
}
