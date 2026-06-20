"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { listSCPs, SCPCard } from "../../lib/api";

export default function BrowsePage() {
  const searchParams = useSearchParams();
  const [scps, setScps] = useState<SCPCard[]>([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    object_class: "",
    entry_type: "",
    sort: "rating",
    search: searchParams.get("search") || "",
  });

  useEffect(() => {
    const search = searchParams.get("search") || "";
    setFilters((f) => ({ ...f, search }));
  }, [searchParams]);

  useEffect(() => {
    setLoading(true);
    listSCPs({
      page,
      per_page: 50,
      object_class: filters.object_class || undefined,
      entry_type: filters.entry_type || undefined,
      sort: filters.sort,
      search: filters.search || undefined,
    })
      .then((data) => {
        setScps(data.items);
        setTotal(data.total);
        setTotalPages(data.total_pages);
      })
      .catch(() => setScps([]))
      .finally(() => setLoading(false));
  }, [page, filters]);

  const classOptions = [
    "Safe",
    "Euclid",
    "Keter",
    "Thaumiel",
    "Apollyon",
    "Archon",
    "Neutralized",
    "Explained",
  ];

  return (
    <div>
      <h1
        style={{
          fontSize: "1.5rem",
          color: "#00ff41",
          marginBottom: 20,
        }}
      >
        SCP ARCHIVE BROWSER
      </h1>

      {/* Filters */}
      <div className="filters">
        <select
          value={filters.object_class}
          onChange={(e) => {
            setFilters({ ...filters, object_class: e.target.value });
            setPage(1);
          }}
        >
          <option value="">All Classes</option>
          {classOptions.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>

        <select
          value={filters.entry_type}
          onChange={(e) => {
            setFilters({ ...filters, entry_type: e.target.value });
            setPage(1);
          }}
        >
          <option value="">All Types</option>
          <option value="scp">SCPs</option>
          <option value="tale">Tales</option>
          <option value="goi-format">GOI Formats</option>
        </select>

        <select
          value={filters.sort}
          onChange={(e) => {
            setFilters({ ...filters, sort: e.target.value });
            setPage(1);
          }}
        >
          <option value="rating">Top Rated</option>
          <option value="title">Title A-Z</option>
          <option value="newest">Newest</option>
          <option value="oldest">Oldest</option>
        </select>

        {filters.search && (
          <span style={{ color: "#888", fontSize: "0.85rem" }}>
            Searching: "{filters.search}"
            <button
              className="btn btn-ghost"
              style={{ marginLeft: 8, fontSize: "0.75rem" }}
              onClick={() => {
                setFilters({ ...filters, search: "" });
                setPage(1);
              }}
            >
              CLEAR
            </button>
          </span>
        )}
      </div>

      {loading ? (
        <div className="loading">Loading entries</div>
      ) : scps.length === 0 ? (
        <div className="error">No entries found</div>
      ) : (
        <>
          <div className="results-count">
            Showing {scps.length} of {total} entries
          </div>

          <div className="scp-grid">
            {scps.map((scp) => (
              <Link
                key={scp.id}
                href={`/scp/${scp.id}`}
                style={{ textDecoration: "none" }}
              >
                <div className="card scp-card">
                  <div className="scp-card-header">
                    <h3>
                      <span style={{ color: "#e0e0e0" }}>{scp.id}</span>
                    </h3>
                    {scp.object_class && (
                      <span
                        className={`object-class ${scp.object_class.toLowerCase()}`}
                      >
                        {scp.object_class}
                      </span>
                    )}
                  </div>
                  <div className="scp-card-meta">
                    {scp.title && <span>{scp.title}</span>}
                    {scp.author && (
                      <span>by {scp.author}</span>
                    )}
                  </div>
                  {scp.description && (
                    <div className="scp-card-desc">
                      {scp.description}
                    </div>
                  )}
                  <div className="scp-card-tags">
                    {scp.tags.slice(0, 6).map((tag) => (
                      <span key={tag} className="tag">
                        {tag}
                      </span>
                    ))}
                  </div>
                  <div className="scp-card-footer">
                    <span>
                      {scp.entry_type.toUpperCase()}
                      {scp.series ? ` | Series ${scp.series}` : ""}
                    </span>
                    <span>Rating: {scp.rating}</span>
                  </div>
                </div>
              </Link>
            ))}
          </div>

          {totalPages > 1 && (
            <div className="pagination">
              <button
                disabled={page <= 1}
                onClick={() => setPage(page - 1)}
              >
                PREV
              </button>
              <span
                style={{
                  padding: "6px 12px",
                  color: "#888",
                  fontSize: "0.85rem",
                }}
              >
                {page} / {totalPages}
              </span>
              <button
                disabled={page >= totalPages}
                onClick={() => setPage(page + 1)}
              >
                NEXT
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}