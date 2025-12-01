export const API_BASE = import.meta.env.VITE_API_BASE;

export async function apiGet(path: string) {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error(`GET ${path} failed: ${res.status}`);
  return res.json();
}

export async function apiPost(path: string, body: any) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  if (!res.ok) throw new Error(`POST ${path} failed: ${res.status}`);
  return res.json();
}

export async function apiDelete(path: string) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "DELETE",
    headers: { "Content-Type": "application/json" }
  });
  if (!res.ok) throw new Error(`DELETE ${path} failed: ${res.status}`);
  return res.json();
}

export async function apiPut(path: string, body: any) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  if (!res.ok) throw new Error(`PUT ${path} failed: ${res.status}`);
  return res.json();
}

// Spots
export async function deleteSpot(id: number) {
  return apiDelete(`/spots/${id}`);
}

export async function updateSpot(id: number, body: any) {
  return apiPut(`/spots/${id}`, body);
}

export async function fetchSpotsForUser(studentId: number) {
  return apiGet(`/spots/user/${studentId}`)
}

// Saved spots / bookmarks
export async function fetchSavedSpots(studentId: number) {
  return apiGet(`/saved-spots/${studentId}`);
}

export async function saveSpot(studentId: number, spotId: number) {
  return apiPost(`/saved-spots`, { student_id: studentId, spot_id: spotId });
}

export async function unsaveSpot(studentId: number, spotId: number) {
  return apiDelete(`/saved-spots/${studentId}/${spotId}`);
}

// Reviews
export async function fetchReviewsForSpot(spotId: number) {
  return apiGet(`/reviews/spot/${spotId}`);
}

export async function fetchReviewsForUser(studentId: number) {
  return apiGet(`/reviews/user/${studentId}`);
}

export async function submitReview(body: { student_id: number; spot_id: number; rating: number; comment: string }) {
  return apiPost(`/reviews`, body);
}

// Votes API
export async function submitVote(studentId: number, spotId: number, categorySlug: string, direction: 1 | -1) {
  return apiPost("/ratings/submit", {
    student_id: studentId,
    spot_id: spotId,
    category_slug: categorySlug,
    direction
  });
}

// User
export async function updateUserProfile(body: { student_id: number; netid?: string; password?: string; current_password?: string }) {
  return apiPut('/auth/update', body)
}

export async function getUserVotes(studentId: number) {
  return apiGet(`/ratings/user/${studentId}`);
}

export async function deleteVote(voteId: number) {
  return apiDelete(`/ratings/vote/${voteId}`);
}
