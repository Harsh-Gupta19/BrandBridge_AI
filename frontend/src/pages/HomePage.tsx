import { Link } from "react-router-dom";

export function HomePage() {
  return (
    <section className="home-page">
      <div className="home-copy">
        <p className="eyebrow">Phase 1 - Engineering Foundation</p>
        <h1>BrandBridge AI</h1>
        <p className="tagline">Connecting creators and brands through intelligent matching.</p>
      </div>

      <div className="portal-grid" aria-label="Portal entry points">
        <Link to="/creator" className="portal-card">
          <span>Creator Portal</span>
          <small>Profiles, rate cards, proposals, and campaign discovery.</small>
        </Link>
        <Link to="/brand" className="portal-card">
          <span>Brand Portal</span>
          <small>Campaigns, creator search, invitations, and approvals.</small>
        </Link>
      </div>
    </section>
  );
}
