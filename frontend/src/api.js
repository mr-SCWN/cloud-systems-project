const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

async function parseResponse(response) {
  if (!response.ok) {
    let message = "Request failed";
    try {
      const data = await response.json();
      message = data.detail || JSON.stringify(data);
    } catch {
      message = await response.text();
    }
    throw new Error(message);
  }
  return response.json();
}

export async function fetchTitles(filters = {}) {
  const params = new URLSearchParams();

  if (filters.type) params.append("type", filters.type);
  if (filters.rating) params.append("rating", filters.rating);
  if (filters.country) params.append("country", filters.country);
  if (filters.title) params.append("title", filters.title);

  params.append("limit", "100");
  params.append("offset", "0");

  const response = await fetch(`${API_URL}/titles?${params.toString()}`);
  return parseResponse(response);
}

export async function createTitle(payload) {
  const response = await fetch(`${API_URL}/titles`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  return parseResponse(response);
}

export async function updateTitle(showId, payload) {
  const response = await fetch(`${API_URL}/titles/${showId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  return parseResponse(response);
}

export async function fetchTopGenres() {
  const response = await fetch(`${API_URL}/stats/top-genres`);
  return parseResponse(response);
}

export async function fetchRecommendations(title) {
  const params = new URLSearchParams({ title, limit: "5" });
  const response = await fetch(`${API_URL}/recommendations?${params.toString()}`);
  return parseResponse(response);
}