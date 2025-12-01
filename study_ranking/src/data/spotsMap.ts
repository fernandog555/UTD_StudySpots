import StudySpot from '../classes/spot'
import { apiGet } from '../api'

const STORAGE_KEY = 'studySpots'

// Default seed is empty; data now comes from the backend
const defaultSeed: StudySpot[] = []

function loadFromStorage(): StudySpot[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return deepCloneArray(defaultSeed)

    const parsed = JSON.parse(raw) as Array<any>
    return (parsed || []).map((o: any) =>
      new StudySpot(
        o.name ?? 'default',
        o.description ?? o.area_description ?? 'default',
        Number(o.id ?? o.spot_id ?? 0),
        Number(o.creator_id ?? o.creatorId ?? 0),
        Number(o.rating ?? o.avg_rating ?? 0),
        o.building_code ?? o.buildingCode ?? '',
        o.area_description ?? o.areaDescription ?? '',
        Number(o.seating_capacity ?? o.seatingCapacity ?? 0),
        Boolean(o.power_outlets ?? o.powerOutlets ?? false),
        Boolean(o.natural_light ?? o.naturalLight ?? false),
        Boolean(o.open_24_7 ?? o.open24_7 ?? false),
        Boolean(o.is_active ?? true),
        Array.isArray(o.categories) ? o.categories.slice() : []
      )
    )
  } catch {
    return deepCloneArray(defaultSeed)
  }
}

function deepCloneArray(src: StudySpot[]) {
  return src.map(s =>
    new StudySpot(
      s.name,
      s.description ?? s.area_description ?? '',
      s.id ?? (s as any).spot_id ?? 0,
      s.creator_id,
      s.rating,
      s.building_code,
      s.area_description,
      s.seating_capacity,
      s.power_outlets,
      s.natural_light,
      s.open_24_7,
      s.is_active,
      s.categories ? s.categories.slice() : []
    )
  )
}

function saveToStorage(spots: StudySpot[]) {
  try {
    const plain = spots.map(s => ({
      id: s.id ?? (s as any).spot_id ?? 0,
      name: s.name,
      description: s.description ?? s.area_description ?? '',
      creator_id: s.creator_id,
      rating: s.rating,
      building_code: s.building_code,
      area_description: s.area_description,
      seating_capacity: s.seating_capacity,
      power_outlets: s.power_outlets,
      natural_light: s.natural_light,
      open_24_7: s.open_24_7,
      is_active: s.is_active,
      categories: s.categories
    }))
    localStorage.setItem(STORAGE_KEY, JSON.stringify(plain))
  } catch {
  }
}

// ALWAYS reload from localStorage instead of caching
export function getStudySpots() {
  return loadFromStorage()
}

export function getSpotById(id: number) {
  const spots = loadFromStorage()
  return spots.find(s => s.id === id) ?? null
}

export function addOrUpdateSpot(input: Partial<StudySpot>) {
  const id = Number((input as any).id ?? 0)
  if (!id) return null

  // Load current spots from storage
  let studySpots = loadFromStorage()

  const existingIndex = studySpots.findIndex(s => s.id === id)
  const newSpot = new StudySpot(
    input.name ?? 'default',
    input.description ?? (input as any).area_description ?? 'default',
    id,
    Number((input as any).creator_id ?? (input as any).creatorId ?? 0),
    Number((input as any).rating ?? (input as any).avg_rating ?? 0),
    input.building_code ?? (input as any).buildingCode ?? '',
    input.area_description ?? (input as any).areaDescription ?? '',
    Number((input as any).seating_capacity ?? (input as any).seatingCapacity ?? 0),
    Boolean((input as any).power_outlets ?? (input as any).powerOutlets ?? false),
    Boolean((input as any).natural_light ?? (input as any).naturalLight ?? false),
    Boolean((input as any).open_24_7 ?? (input as any).open24_7 ?? false),
    Boolean((input as any).is_active ?? true),
    Array.isArray((input as any).categories) ? (input as any).categories.slice() : []
  )

  if (existingIndex >= 0) {
    studySpots[existingIndex] = newSpot
  } else {
    studySpots.push(newSpot)
  }

  saveToStorage(studySpots)
  return newSpot
}

export function mapApiSpot(raw: any): StudySpot {
  return new StudySpot(
    raw?.name ?? 'Unnamed spot',
    raw?.area_description ?? raw?.description ?? '',
    Number(raw?.spot_id ?? raw?.id ?? 0),
    Number(raw?.creator_id ?? raw?.student_id ?? 0),
    Number(raw?.avg_rating ?? raw?.rating ?? 0),
    raw?.building_code ?? '',
    raw?.area_description ?? '',
    Number(raw?.seating_capacity ?? 0),
    Boolean(raw?.power_outlets),
    Boolean(raw?.natural_light),
    Boolean(raw?.open_24_7),
    raw?.is_active !== false,
    Array.isArray(raw?.categories) ? raw.categories.slice() : []
  )
}

export async function fetchAndStoreSpots(): Promise<StudySpot[]> {
  const data = await apiGet('/spots')
  const mapped = Array.isArray(data) ? data.map(mapApiSpot) : []
  saveToStorage(mapped)
  return mapped
}
