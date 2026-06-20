/** API client for the SCP Archive backend. */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface SCPCard {
  id: string;
  title: string;
  object_class: string | null;
  tags: string[];
  author: string | null;
  rating: number;
  entry_type: string;
  description: string;
  series: number | null;
}

export interface SCPDetail {
  id: string;
  title: string;
  url: string;
  object_class: string | null;
  secondary_class: string | null;
  containment_procedures: string;
  description: string;
  tags: string[];
  author: string | null;
  rating: number;
  created_date: string | null;
  entry_type: string;
  related_scps: string[];
  series: number | null;
  image_urls: string[];
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface TagCount {
  name: string;
  count: number;
}

export interface ArchiveStats {
  total_entries: number;
  scps: number;
  tales: number;
  goi_formats: number;
  total_tags: number;
  class_distribution: Record<string, number>;
}

async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${endpoint}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`API error (${res.status}): ${err}`);
  }
  return res.json();
}

export async function listSCPs(params?: {
  page?: number; per_page?: number; object_class?: string;
  entry_type?: string; series?: number; tag?: string;
  search?: string; sort?: string;
}): Promise<PaginatedResponse<SCPCard>> {
  const sp = new URLSearchParams();
  if (params) {
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== "") sp.set(k, String(v));
    });
  }
  return fetchAPI(`/api/scps${sp.toString() ? `?${sp}` : ""}`);
}

export async function getSCP(id: string): Promise<SCPDetail> {
  return fetchAPI(`/api/scps/${encodeURIComponent(id)}`);
}

export async function getRelated(id: string): Promise<{ items: SCPCard[]; count: number }> {
  return fetchAPI(`/api/scps/${encodeURIComponent(id)}/related`);
}

export async function getTags(): Promise<{ items: TagCount[]; total: number }> {
  return fetchAPI("/api/tags?min_count=1&limit=100");
}

export async function getStats(): Promise<ArchiveStats> {
  return fetchAPI("/api/tags/stats");
}

export async function askAI(question: string, contextIds?: string[]) {
  return fetchAPI<{ question: string; answer: string }>("/api/ai/ask", {
    method: "POST", body: JSON.stringify({ question, context_ids: contextIds }),
  });
}

export async function recommendAI(scpId: string) {
  return fetchAPI<{ based_on: string; recommendation: string }>("/api/ai/recommend", {
    method: "POST", body: JSON.stringify({ scp_id: scpId }),
  });
}

export async function aiStatus() {
  return fetchAPI<{ available: boolean; message: string }>("/api/ai/status");
}