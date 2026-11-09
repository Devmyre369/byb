
import { useEffect, useState } from "react";
import { getHubs, type Hub, type HubType } from "../api/hubs";
import "./HubDiscoverPage.css";

const hubTypes: {
  label: string;
  value: HubType | "all";
}[] = [
  { label: "All Hubs", value: "all" },
  { label: "Colleges", value: "college" },
  { label: "Clubs", value: "club" },
  { label: "Organisations", value: "organisation" },
  { label: "Communities", value: "community" },
];

function HubDiscoverPage() {
  const [hubs, setHubs] = useState<Hub[]>([]);
  const [search, setSearch] = useState("");
  const [city, setCity] = useState("");
  const [activeType, setActiveType] = useState<HubType | "all">("all");

  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState("");

  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);
  const [total, setTotal] = useState(0);

  async function loadHubs(pageNumber = 1) {
    try {
      if (pageNumber === 1) {
        setLoading(true);
      } else {
        setLoadingMore(true);
      }

      setError("");

      const response = await getHubs({
        page: pageNumber,
        pageSize: 20,
        search: search.trim(),
        city: city.trim(),
        hubType: activeType,
      });

      setHubs((previous) =>
        pageNumber === 1
          ? response.results
          : [...previous, ...response.results]
      );

      setTotal(response.count);
      setHasMore(Boolean(response.next));
      setPage(pageNumber);
    } catch (error) {
      console.error("Failed to load Hubs:", error);
      setError("We couldn't load Hubs right now. Please try again.");
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  }

  useEffect(() => {
    const timeout = window.setTimeout(() => {
      void loadHubs(1);
    }, 250);

    return () => window.clearTimeout(timeout);
  }, [search, city, activeType]);

  function getHubTypeLabel(type: HubType) {
    return type.charAt(0).toUpperCase() + type.slice(1);
  }

  return (
    <div className="content hub-discover-page">
      <header className="hub-discover-header">
        <div>
          <span className="event-category">
            BEYOND YOUR BUBBLE
          </span>

          <h1>Find your people.</h1>

          <p>
            Discover colleges, clubs, organisations and communities.
            Join spaces that bring people and real-world experiences together.
          </p>
        </div>

        <div className="hub-header-mark" aria-hidden="true">
          <span>H</span>
        </div>
      </header>

      <section className="hub-search-panel">
        <label className="hub-search-field">
          <span>Search Hubs</span>

          <input
            type="search"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search by Hub name or description"
          />
        </label>

        <label className="hub-search-field hub-city-field">
          <span>City</span>

          <input
            type="text"
            value={city}
            onChange={(event) => setCity(event.target.value)}
            placeholder="e.g. Lucknow"
          />
        </label>
      </section>

      <section className="hub-results-section">
        <div
          className="hub-filter-row"
          aria-label="Filter Hubs by type"
        >
          {hubTypes.map((type) => (
            <button
              type="button"
              key={type.value}
              className={`hub-filter-chip ${
                activeType === type.value ? "active" : ""
              }`}
              onClick={() => setActiveType(type.value)}
              aria-pressed={activeType === type.value}
            >
              {type.label}
            </button>
          ))}
        </div>

        <div className="hub-section-heading">
          <div>
            <span className="section-eyebrow">
              YOUR NEXT COMMUNITY
            </span>

            <h2>Explore Hubs</h2>

            <p className="section-subtitle">
              Find a community that matches your interests.
            </p>
          </div>

          {!loading && !error && (
            <span className="hub-result-count">
              {total} {total === 1 ? "Hub" : "Hubs"}
            </span>
          )}
        </div>

        {loading ? (
          <div className="hub-state">
            Loading Hubs...
          </div>
        ) : error ? (
          <div className="hub-state hub-error-state">
            <h3>Unable to load Hubs</h3>

            <p>{error}</p>

            <button
              type="button"
              className="hub-primary-button"
              onClick={() => void loadHubs(1)}
            >
              Try again
            </button>
          </div>
        ) : hubs.length > 0 ? (
          <>
            <div className="hub-grid">
              {hubs.map((hub) => (
                <article
                  className="hub-card"
                  key={hub.id}
                >
                  <div className="hub-card-cover">
                    {hub.cover_image ? (
                      <img
                        src={hub.cover_image}
                        alt={`${hub.name} cover`}
                        loading="lazy"
                      />
                    ) : (
                      <div className="hub-cover-placeholder">
                        <span>BYB.</span>
                      </div>
                    )}

                    <span className="hub-type-label">
                      {getHubTypeLabel(hub.hub_type)}
                    </span>
                  </div>

                  <div className="hub-card-content">
                    <div className="hub-card-identity">
                      {hub.logo ? (
                        <img
                          className="hub-logo"
                          src={hub.logo}
                          alt={`${hub.name} logo`}
                          loading="lazy"
                        />
                      ) : (
                        <div className="hub-logo hub-logo-placeholder">
                          {hub.name.charAt(0).toUpperCase()}
                        </div>
                      )}

                      <div className="hub-card-title">
                        <h3>{hub.name}</h3>

                        <span>
                          {hub.city || "Location not specified"}
                        </span>
                      </div>
                    </div>

                    <p className="hub-card-description">
                      {hub.description || "A community on BYB."}
                    </p>

                    <div className="hub-card-footer">
                      <span>
                        {hub.member_count}{" "}
                        {hub.member_count === 1
                          ? "member"
                          : "members"}
                      </span>

                      <span>
                        {hub.membership_policy === "automatic"
                          ? "Open to join"
                          : "Request to join"}
                      </span>
                    </div>

                    {hub.current_membership && (
                      <div className="hub-membership-status">
                        {hub.current_membership.status === "active"
                          ? "You're a member"
                          : hub.current_membership.status === "pending"
                            ? "Request pending"
                            : "Previous request rejected"}
                      </div>
                    )}
                  </div>
                </article>
              ))}
            </div>

            {hasMore && (
              <div className="hub-load-more">
                <button
                  type="button"
                  className="hub-secondary-button"
                  disabled={loadingMore}
                  onClick={() => void loadHubs(page + 1)}
                >
                  {loadingMore
                    ? "Loading..."
                    : "Load more Hubs"}
                </button>
              </div>
            )}
          </>
        ) : (
          <div className="hub-state hub-empty-state">
            <h3>No Hubs found</h3>

            <p>
              Try another search, city or Hub category.
            </p>

            <button
              type="button"
              className="hub-secondary-button"
              onClick={() => {
                setSearch("");
                setCity("");
                setActiveType("all");
              }}
            >
              Clear filters
            </button>
          </div>
        )}
      </section>
    </div>
  );
}

export default HubDiscoverPage;
