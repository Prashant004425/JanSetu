export type RequestAnalysis = {
  language: string;
  translated_text: string;
  understanding: string;
  categories: string[];
  category: string;
  subcategory: string;
  location: string | null;
  issue: string;
  urgency: string;
  severity: string;
  confidence: number;
  priority_score: number;
  priority_label: string;
  similar_request_count: number;
};

export type CitizenRequest = RequestAnalysis & {
  id: number;
  text: string;
  request_id: string;
  risk_level: string;
  assigned_to: string | null;
  progress_percent: number;
  government_notes: string;
  completion_notes: string;
  completed_at: string | null;
  status: string;
  created_at: string;
  updated_at: string;
};

export type DashboardSummary = {
  total_requests: number;
  completed_requests: number;
  pending_requests: number;
  high_priority_requests: number;
  active_hotspots: number;
  top_category: string;
  top_location: string;
};

export type WorkSummary = {
  total: number; pending: number; in_progress: number; on_hold: number;
  completed: number; cancelled: number; high_risk: number; critical_risk: number;
  urgent: number; completion_rate: number; average_resolution_days: number | null;
};

export type RequestInput = {
  text: string;
  location?: string;
  selected_language?: string;
};

const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || '/jan-setu-api/api'
).replace(/\/$/, '');

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...init?.headers,
    },
  });

  if (!response.ok) {
    const body = await response.text();
    let message = body;
    try {
      const parsed = JSON.parse(body) as { detail?: string };
      message = parsed.detail ?? body;
    } catch {
      // Keep the plain response body when the server did not return JSON.
    }
    throw new Error(message || `Request failed with status ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export function previewRequest(input: RequestInput) {
  return request<RequestAnalysis>('/requests/preview', {
    method: 'POST',
    body: JSON.stringify(input),
  });
}

export function saveRequest(input: RequestInput) {
  return request<CitizenRequest>('/requests/analyze', {
    method: 'POST',
    body: JSON.stringify(input),
  });
}

export function listRequests() {
  return request<CitizenRequest[]>('/requests?limit=20');
}

export function getDashboardSummary() {
  return request<DashboardSummary>('/requests/summary');
}

export function updateRequestStatus(id: number, status: string) {
  return request<CitizenRequest>(`/requests/${id}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ status }),
  });
}

export function getWorkSummary() {
  return request<WorkSummary>('/government/dashboard/summary');
}

export function listGovernmentRequests(params: { status?: string; risk?: string; urgency?: string; search?: string } = {}) {
  const query = new URLSearchParams(Object.entries(params).filter((entry): entry is [string, string] => Boolean(entry[1])));
  return request<CitizenRequest[]>(`/government/requests${query.toString() ? `?${query}` : ''}`);
}

export function updateGovernmentStatus(id: number, payload: { status: string; notes?: string; progress_percent?: number }) {
  return request<CitizenRequest>(`/government/requests/${id}/status`, { method: 'PATCH', body: JSON.stringify(payload) });
}

export function updateGovernmentProgress(id: number, payload: { progress_percent: number; notes?: string }) {
  return request<CitizenRequest>(`/government/requests/${id}/progress`, { method: 'PATCH', body: JSON.stringify(payload) });
}

export function updateGovernmentAssignment(id: number, assigned_to: string | null) {
  return request<CitizenRequest>(`/government/requests/${id}/assignment`, { method: 'PATCH', body: JSON.stringify({ assigned_to }) });
}