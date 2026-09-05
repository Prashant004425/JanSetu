export type RequestAnalysis = {
  language: string;
  translated_text: string;
  understanding: string;
  categories: string[];
  category: string;
  location: string;
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
  status: string;
  created_at: string;
};

export type DashboardSummary = {
  total_requests: number;
  high_priority_requests: number;
  active_hotspots: number;
  top_category: string;
  top_location: string;
};

export type RequestInput = {
  text: string;
  location?: string;
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
    const message = await response.text();
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