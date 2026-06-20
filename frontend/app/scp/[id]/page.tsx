"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { getSCP, SCPDetail, getRelated, SCPCard, recommendAI, aiStatus } from "../../../lib/api";

export default function SCPDetailPage() {
  const params = useParams();
  const id = params.id as string;
  const [scp, setScp] = useState<SCPDetail | null>(null);
  const [related, setRelated] = useState<SCPCard[]>([]);
  const [loading, setLoading] = useState(true);
  const [recommendation, setRecommendation] = useState<string | null>(null);
  const [aiAvailable, setAiAvailable] = useState(false);
  const [recLoading, setRecLoading] = useState(false);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    Promise.all([
      getSCP(id),
      getRelated(id).then((r) => setRelated(r.items)).catch(() => {}),
      aiStatus().then((s) => setAiAvailable(s.available)).catch(() => {}),
    ])
      .then(([scpData]) => setScp(scpData))
      .catch(() => setScp(null))
      .finally(() => setLoading(false));
  }, [id]);

  const handleRecommend = async () => {
    setRecLoading(true);
    try {
      const res = await recommendAI(id);
      setRecommendation(res.recommendation);
    } catch {
      setRecommendation("Recommendation unavailable.");
    }
    setRecLoading(false);
  };

  if (loading) return <div className="loading">Loading {id}</div>;
  if (!scp) return <div className="error">SCP not found</div>;

  return (
    <div className="scp-detail">
      <Link
        href="/browse"
        style={{ color: "#555", fontSize: "0.85rem", marginBottom: 16, display: "inline-block" }}
      >
        &larr; Back to Browse
      </Link>

      <div className="scp-detail-header">
        <h1>{scp.id}</h1>
        <div className="meta">
          {scp.object_class && (
            <span className={`object-class ${scp.object_class.toLowerCase()}`}>
              {scp.object_class}
            </span>
          )}
          {scp.secondary_class && (
            <span className={`object-class ${scp.secondary_class.toLowerCase()}`}>
              {scp.secondary_class}
            </span>
          )}
          <span>Rating: {scp.rating}</span>
          {scp.author && <span>by {scp.author}</span>}
          {scp.created_date && <span>{scp.created_date}</span>}
          {scp.series && <span>Series {scp.series}</span>}
        </div>
      </div>

      {scp.containment_procedures && (
        <div className="scp-section">
          <h2>SPECIAL CONTAINMENT PROCEDURES</h2>
          <div className="content">{scp.containment_procedures}</div>
        </div>
      )}

      <div className="scp-section">
        <h2>DESCRIPTION</h2>
        <div className="content">{scp.description}</div>
      </div>

      {scp.tags.length > 0 && (
        <div className="scp-section">
          <h2>TAGS</h2>
          <div>
            {scp.tags.map((tag) => (
              <Link key={tag} href={`/browse?tag=${tag}`} className="tag">
                {tag}
              </Link>
            ))}
          </div>
        </div>
      )}

      {related.length > 0 && (
        <div className="scp-section">
          <h2>RELATED SCPs</h2>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {related.slice(0, 10).map((r) => (
              <Link
                key={r.id}
                href={`/scp/${r.id}`}
                style={{ color: "#888", fontSize: "0.9rem" }}
              >
                {r.id} - {r.title}
              </Link>
            ))}
          </div>
        </div>
      )}

      {aiAvailable && (
        <div className="scp-section">
          <h2>AI RECOMMENDATIONS</h2>
          <button
            className="btn btn-primary"
            onClick={handleRecommend}
            disabled={recLoading}
          >
            {recLoading ? "Thinking..." : "Get AI Recommendations"}
          </button>
          {recommendation && (
            <div
              className="content"
              style={{ marginTop: 12, whiteSpace: "pre-wrap" }}
            >
              {recommendation}
            </div>
          )}
        </div>
      )}
    </div>
  );
}