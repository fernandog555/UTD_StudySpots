import Review from '../classes/reviews'
import { fetchReviewsForSpot as fetchSpotReviewsApi, fetchReviewsForUser as fetchReviewsForUserApi, submitReview as submitReviewApi } from '../api'

export let reviewsMap: Record<number, Review[]> = {}
const inflight: Record<number, Promise<Review[]>> = {}

function mapReview(raw: any): Review {
  const author = raw?.author || raw?.netid || 'anonymous'
  const text = raw?.text || raw?.comment || ''
  const rating = Number(raw?.rating ?? 0)
  const createdAt = (raw?.created_at as string) || (raw?.date as string) || new Date().toISOString()
  const date = createdAt.slice(0, 10)
  const spotId = Number(raw?.spot_id ?? 0)
  const id = Number(raw?.id ?? raw?.vote_id ?? 0)
  return new Review(author, text, rating, date, spotId, id)
}

export function getReviewsForSpot(id: number): Review[] {
  return reviewsMap[id] || []
}

export async function fetchReviewsForSpot(id: number): Promise<Review[]> {
  if (!id) return []
  if (inflight[id]) return inflight[id]

  inflight[id] = (async () => {
    const data = await fetchSpotReviewsApi(id)
    const mapped = Array.isArray(data) ? data.map(mapReview) : []
    reviewsMap[id] = mapped
    return mapped
  })()

  try {
    return await inflight[id]
  } finally {
    delete inflight[id]
  }
}

export async function fetchUserReviews(studentId: number): Promise<Review[]> {
  if (!studentId) return []
  const data = await fetchReviewsForUserApi(studentId)
  const mapped = Array.isArray(data) ? data.map(mapReview) : []
  // prime map by spot id
  mapped.forEach(r => {
    if (!reviewsMap[r.spot_id]) reviewsMap[r.spot_id] = []
    const arr = reviewsMap[r.spot_id]
    const idx = arr.findIndex(existing => existing.id === r.id)
    if (idx >= 0) arr[idx] = r
    else arr.push(r)
  })
  return mapped
}

export async function addReview(reviewInput: { student_id: number; spot_id: number; rating: number; text: string }): Promise<Review> {
  const payload = {
    student_id: reviewInput.student_id,
    spot_id: reviewInput.spot_id,
    rating: reviewInput.rating,
    comment: reviewInput.text,
  }

  const created = await submitReviewApi(payload)
  const mapped = mapReview(created)

  const spotId = mapped.spot_id
  if (!reviewsMap[spotId]) reviewsMap[spotId] = []
  const idx = reviewsMap[spotId].findIndex(r => r.id === mapped.id)
  if (idx >= 0) reviewsMap[spotId][idx] = mapped
  else reviewsMap[spotId].unshift(mapped)

  return mapped
}

export async function primeReviewsForSpots(spotIds: number[]): Promise<void> {
  const unique = Array.from(new Set(spotIds.filter(Boolean)))
  await Promise.all(unique.map(id => fetchReviewsForSpot(id)))
}

export function deleteReviewsForSpot(spotId: number): void {
  if (reviewsMap[spotId]) {
    delete reviewsMap[spotId]
  }
}
