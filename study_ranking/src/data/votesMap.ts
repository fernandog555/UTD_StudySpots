import { submitVote as submitVoteApi, deleteVote as deleteVoteApi, getUserVotes } from '@/api'

interface CategoryVotes {
  voters: Record<string, VoteDirection>
}

export type SpotVotes = Record<string, CategoryVotes>
const STORAGE_KEY = 'votesMap'

type VoteDirection = 1 | -1

const DEFAULT_STATE: Record<number, SpotVotes> = {}

// Backend votes storage
let backendVotes: Record<number, any[]> = {}
let studentId: number | null = null

function load(): Record<number, SpotVotes> {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) {
      save(DEFAULT_STATE)
      return DEFAULT_STATE
    }

    const parsed = JSON.parse(raw)
    if (!parsed || Object.keys(parsed).length === 0) {
      save(DEFAULT_STATE)
      return DEFAULT_STATE
    }

    return parsed
  } catch {
    try { save(DEFAULT_STATE) } catch { }
    return DEFAULT_STATE
  }
}

function save(state: Record<number, SpotVotes>) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
  } catch {
  }
}

const state = load()

function ensureSpot(spotId: number) {
  if (!state[spotId]) state[spotId] = {}
  return state[spotId]
}

function ensureCategory(spotId: number, category: string) {
  const sp = ensureSpot(spotId)
  if (!sp[category]) sp[category] = { voters: {} }
  return sp[category]
}

export function getVotesForSpot(spotId: number): SpotVotes {
  return state[spotId] ?? {}
}

export function getCounts(spotId: number, category: string) {
  const cat = state[spotId]?.[category]
  if (!cat) return { up: 0, down: 0, net: 0 }
  let up = 0
  let down = 0
  for (const v of Object.values(cat.voters)) {
    if (v === 1) up++
    else if (v === -1) down++
  }
  return { up, down, net: up - down }
}

export function toggleVote(spotId: number, category: string, dir: VoteDirection) {
  const username = localStorage.getItem('username')

  if (!username) {
    return getCounts(spotId, category)
  }

  const cat = ensureCategory(spotId, category)
  const existing = cat.voters[username]

  if (existing === dir) {
    delete cat.voters[username]
  } else {
    cat.voters[username] = dir
  }

  save(state)
  window.dispatchEvent(new CustomEvent('votes-changed', { detail: { spotId, category } }))
  return getCounts(spotId, category)
}

export function deleteVotesForSpot(spotId: number): void {
  if (state[spotId]) {
    delete state[spotId]
    save(state)
  }
}

// Backend sync functions
export function setStudentId(id: number | null) {
  studentId = id
}

export async function loadUserVotesFromBackend(id: number) {
  try {
    const votes = await getUserVotes(id)
    backendVotes = {}
    
    // Organize votes by spotId
    votes.forEach((vote: any) => {
      if (!backendVotes[vote.spot_id]) {
        backendVotes[vote.spot_id] = []
      }
      backendVotes[vote.spot_id]!.push(vote)
    })
    
    return backendVotes
  } catch (error) {
    console.error('Failed to load votes from backend:', error)
    return {}
  }
}

export function getBackendVote(spotId: number, categorySlug: string) {
  const spotVotes = backendVotes[spotId] || []
  return spotVotes.find((v: any) => v.slug === categorySlug)
}

export async function submitVoteToBackend(studentId: number, spotId: number, categorySlug: string, direction: VoteDirection) {
  try {
    const result = await submitVoteApi(studentId, spotId, categorySlug, direction)
    
    // Update backend votes cache
    if (!backendVotes[spotId]) {
      backendVotes[spotId] = []
    }
    
    // Remove old vote if exists
    backendVotes[spotId] = backendVotes[spotId].filter((v: any) => v.slug !== categorySlug)
    
    // Add new vote
    backendVotes[spotId].push(result)
    
    return result
  } catch (error) {
    console.error('Failed to submit vote to backend:', error)
    throw error
  }
}

export async function deleteVoteFromBackend(voteId: number, spotId: number, categorySlug: string) {
  try {
    await deleteVoteApi(voteId)
    
    // Update backend votes cache
    if (backendVotes[spotId]) {
      backendVotes[spotId] = backendVotes[spotId].filter((v: any) => v.slug !== categorySlug)
    }
  } catch (error) {
    console.error('Failed to delete vote from backend:', error)
    throw error
  }
}

export default {
  getVotesForSpot,
  getCounts,
  toggleVote,
  deleteVotesForSpot,
  setStudentId,
  loadUserVotesFromBackend,
  getBackendVote,
  submitVoteToBackend,
  deleteVoteFromBackend
}
