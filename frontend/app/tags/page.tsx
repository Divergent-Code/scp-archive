"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getTags, getStats, TagCount, ArchiveStats } from "../../lib/api";

export default function TagsPage() {
  const [tags, setTags] = useState<TagCount[]>([]);
  const [stats, setStats] = useState<ArchiveStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getTags(), getStats()])
      .then(([tagData, statsData]) => {
        setTags(tagData.items);
        setStats(statsData);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const maxCount = tags.length > 0 ? Math.max(...tags.map((t) => t.count)) : 1;

  return (
    <div>
      <h1
        style={{
          fontSize: "1.5rem",
          color: "#00ff41",
          marginBottom: 8,
        }}
      >
        ARCHIVE TAGS
      </h1>
      <p style={{ color: "#888", fontSize: "0.85rem", marginBottom: 24 }}>
        Browse SCP entries by tag and category.
      </p>

      {/* Stats cards */}
      {stats && (
        <div className="stats-grid" style={{ marginBottom: 32 }}>
          <div className="stat-card">
            <div className="stat-value">{stats.total_entries}</div>
            <div className="stat-label">Total Entries</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.total_tags}</div>
            <div className="stat-label">Total Tags</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.scps}</div>
            <div className="stat-label">SCPs</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.tales}</div>
            <div className="stat-label">Tales</div>
          </div>
        </div>
      )}

      {/* Class distribution */}
      {stats && Object.keys(stats.class_distribution).length > 0 && (
        <div style={{ marginBottom: 32 }}>
          <h2
            style={{
              fontSize: "1rem",
              color: "#ffb000",
              marginBottom: 12,
              borderBottom: "1px solid #222",
              paddingBottom: 8,
            }}
          >
            OBJECT CLASS DISTRIBUTION
          </h2>
          <div
            style={{
              display: "flex",
              gap: 12,
              flexWrap: "wrap",
            }}
          >
            {Object.entries(stats.class_distribution).map(([cls, count]) => (
              <div
                key={cls}
                className="card"
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 12,
                  padding: "12px 16px",
                }}
              >
                <span className={`object-class ${cls.toLowerCase()}`}>
                  {cls}
                </span>
                <span style={{ color: "#888", fontSize: "0.9rem" }}>
                  {count} entries
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tag cloud */}
      <h2
        style={{
          fontSize: "1rem",
          color: "#ffb000",
          marginBottom: 12,
          borderBottom: "1px solid #222",
          paddingBottom: 8,
        }}
      >
        TAG CLOUD
      </h2>

      {loading ? (
        <div className="loading">Loading tags</div>
      ) : tags.length === 0 ? (
        <div className="error">No tags found</div>
      ) : (
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
          {tags.map((tag) => {
            const size = 0.8 + (tag.count / maxCount) * 0.8;
            return (
              <Link
                key={tag.name}
                href={`/browse?tag=${tag.name}`}
                className="tag"
                style={{
                  fontSize: `${size}rem`,
                  borderColor:
                    tag.count > maxCount * 0.5
                      ? "rgba(0, 255, 65, 0.4)"
                      : undefined,
                }}
              >
                {tag.name} ({tag.count})
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}