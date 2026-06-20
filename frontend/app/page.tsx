"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getStats } from "../lib/api";

interface Stats {
  total_entries: number;
  scps: number;
  tales: number;
  goi_formats: number;
  total_tags: number;
  class_distribution: Record<string, number>;
}

export default function HomePage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getStats()
      .then(setStats)
      .catch(() => setStats(null))
      .finally(() => setLoading(false));
  }, []);

  const featured = [
    { id: "SCP-173", title: "The Sculpture", class: "Euclid" },
    { id: "SCP-682", title: "Hard-to-Destroy Reptile", class: "Keter" },
    { id: "SCP-999", title: "The Tickle Monster", class: "Safe" },
    { id: "SCP-096", title: "The Shy Guy", class: "Euclid" },
    { id: "SCP-914", title: "The Clockworks", class: "Safe" },
    { id: "SCP-2000", title: "The Deus Ex Machina", class: "Thaumiel" },
  ];

  return (
    <div>
      {/* Hero */}
      <div style={{ textAlign: "center", padding: "60px 0 40px" }}>
        <h1
          style={{
            fontSize: "2.5rem",
            color: "#00ff41",
            marginBottom: 12,
            letterSpacing: 2,
          }}
        >
          SCP FOUNDATION ARCHIVE
        </h1>
        <p
          style={{
            color: "#888",
            fontSize: "0.95rem",
            maxWidth: 600,
            margin: "0 auto",
            lineHeight: 1.8,
          }}
        >
          An interactive database of SCP Foundation articles, Foundation Tales,
          and Groups of Interest. Explore the anomalies with our AI guide.
        </p>
      </div>

      {/* Stats */}
      {loading ? (
        <div className="loading">Loading archive statistics</div>
      ) : stats ? (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-value">{stats.total_entries}</div>
            <div className="stat-label">Total Entries</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.scps}</div>
            <div className="stat-label">SCPs</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.tales}</div>
            <div className="stat-label">Tales</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.goi_formats}</div>
            <div className="stat-label">GOI Formats</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.total_tags}</div>
            <div className="stat-label">Tags</div>
          </div>
        </div>
      ) : (
        <div style={{ textAlign: "center", padding: 20, color: "#555" }}>
          No data loaded yet. Run the scraper and import the data into the
          database.
        </div>
      )}

      {/* Featured SCPs */}
      <h2
        style={{
          fontSize: "1.1rem",
          color: "#ffb000",
          marginBottom: 16,
          borderBottom: "1px solid #222",
          paddingBottom: 8,
        }}
      >
        FEATURED ANOMALIES
      </h2>

      <div className="scp-grid">
        {featured.map((scp) => (
          <Link
            key={scp.id}
            href={`/scp/${scp.id}`}
            style={{ textDecoration: "none" }}
          >
            <div className="card scp-card">
              <div className="scp-card-header">
                <h3>{scp.id}</h3>
                <span className={`object-class ${scp.class.toLowerCase()}`}>
                  {scp.class}
                </span>
              </div>
              <div className="scp-card-desc" style={{ marginTop: 4 }}>
                {scp.title}
              </div>
              <div className="scp-card-footer">
                <span>Click to view details</span>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {/* Quick actions */}
      <div
        style={{
          display: "flex",
          gap: 12,
          justifyContent: "center",
          marginTop: 40,
          flexWrap: "wrap",
        }}
      >
        <Link href="/browse" className="btn btn-primary">
          BROWSE ALL SCPs
        </Link>
        <Link href="/ai-guide" className="btn">
          ASK THE AI GUIDE
        </Link>
        <Link href="/tags" className="btn">
          EXPLORE TAGS
        </Link>
      </div>
    </div>
  );
}