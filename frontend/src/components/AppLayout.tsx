import { NavLink, Outlet } from "react-router-dom";

const navigationItems = [
  { to: "/", label: "Home" },
  { to: "/creator", label: "Creator Portal" },
  { to: "/brand", label: "Brand Portal" },
  { to: "/campaigns", label: "Campaigns" },
  { to: "/creators", label: "Creators" },
  { to: "/recommendations", label: "Recommendations" },
  { to: "/proposals", label: "Proposals" },
];

export function AppLayout() {
  return (
    <div className="app-shell">
      <header className="app-header">
        <NavLink to="/" className="brand-mark">
          BrandBridge AI
        </NavLink>
        <nav className="app-nav" aria-label="Primary navigation">
          {navigationItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
              end={item.to === "/"}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </header>
      <main className="app-main">
        <Outlet />
      </main>
    </div>
  );
}
