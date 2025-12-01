<template>
  <div>
    <div v-if="showHeader" class="flex items-center justify-between mb-4">
      <h2 class="text-2xl">Study Spots</h2>
      <Filter v-model="selectedFilter"
              :options="filterOptions"
              id="spot-filter"
              label="Filter study spots" />
    </div>

    <div class="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
      <div v-for="spot in sortedSpots"
           :key="spot.id"
           class="p-4 border rounded-md shadow bg-(--bg) relative flex flex-col">
        <!-- review (icon) -->
        <button title="Review"
                @click="handleReport(spot)"
                class="absolute top-2 right-12 w-8 h-8 flex items-center justify-center rounded-md hover:bg-black/10 transition"
                aria-label="Review this spot">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
               class="w-5 h-5 text-(--dark5)" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 20h9" />
            <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 3.5a2.121 2.121 0 1 1 3 3L8 18l-4 1 1-4 11.5-11.5z" />
          </svg>
        </button>

        <!-- bookmark button -->
        <button :aria-pressed="!!bookmarks[spot.id]"
                :title="bookmarks[spot.id] ? 'Remove bookmark' : 'Add bookmark'"
                @click="toggleBookmark(spot.id)"
                class="absolute top-2 right-2 w-8 h-8 flex items-center justify-center rounded-md hover:bg-black/10 transition">
          <svg v-if="bookmarks[spot.id]" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
               class="w-5 h-5 text-yellow-400 fill-current" aria-hidden="true">
            <path d="M6 2a1 1 0 0 0-1 1v18l7-4 7 4V3a1 1 0 0 0-1-1H6z" />
          </svg>

          <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
               class="w-5 h-5 text-yellow-400" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 2a1 1 0 0 0-1 1v18l7-4 7 4V3a1 1 0 0 0-1-1H6z" />
          </svg>
        </button>

        <div class="flex-1">
          <h2 class="text-xl font-bold pr-20">{{ spot.name }}</h2>
          <p class="mt-2">Rating: {{ formatRating(combinedRating(spot)) }} / 5</p>
          <p class="mt-2">{{ spot.description }}</p>
        </div>

        <div class="mt-4 flex flex-wrap gap-2">
          <button @click="$emit('view-details', spot)"
                  class="px-6 py-2 rounded-md text-base text-center hover:cursor-pointer hover:bg-(--fg_gutter) border">
            View Details
          </button>

          <!-- Reviews button -->
          <button @click="$emit('view-reviews', spot)"
                  class="px-6 py-2 rounded-md text-base text-center hover:cursor-pointer hover:bg-(--fg_gutter) border">
            Reviews
          </button>

          <!-- Votes button -->
          <button @click="openVotes(spot)"
                  class="px-6 py-2 rounded-md text-base text-center hover:cursor-pointer hover:bg-(--fg_gutter) border">
            Vote
          </button>
        </div>
      </div>
    </div>

    <!-- Reusable auth modal -->
    <Auth v-model="showAuthModal"
          :title="authModalTitle"
          :message="authModalMessage"
          @confirm="goToAccount" />

    <!-- Review modal -->
    <Review v-if="showReviewModal" :spot="currentReviewSpot" @close="closeReviewModal" @submitted="onReviewSubmitted" />

    <!-- Votes modal -->
    <Votes :spot="currentVoteSpot" :visible="showVotesModal" @update:visible="showVotesModal = $event" @require-auth="onVotesRequireAuth" />
  </div>
</template>

<script setup lang="ts">
  import { ref, onMounted, onBeforeUnmount, computed, watch } from 'vue'
  import { useRouter } from 'vue-router'
  import StudySpot from '../classes/spot.ts'
  import { getReviewsForSpot, addReview, primeReviewsForSpots, fetchReviewsForSpot } from '../data/reviewsMap'
  import { addOrUpdateSpot } from '../data/spotsMap'
  import Auth from '../views/Auth.vue'
  import Review from './Review.vue'
  import Filter from './Filter.vue'
  import Votes from './Votes.vue'
  import { fetchSavedSpots, saveSpot, unsaveSpot } from '@/api'

  const props = defineProps<{
    spots: StudySpot[]
    modelValue?: string
    showHeader?: boolean
  }>()

  const emit = defineEmits<{
    (e: 'update:modelValue', v: string): void
    (e: 'view-details', spot: StudySpot): void
    (e: 'view-reviews', spot: StudySpot): void
    (e: 'report-spot', spot: StudySpot): void
  }>()

  const router = useRouter()
  const currentUser = ref<{ student_id: number; netid?: string } | null>(null)
  const bookmarks = ref<Record<number, boolean>>({})

  const showHeader = props.showHeader === undefined ? true : props.showHeader

  // Exposed filter options
  const filterOptions = [
    { value: 'most-reviews', label: 'Most reviews' },
    { value: 'least-reviews', label: 'Least reviews' },
    { value: 'highest', label: 'Highest rating' },
    { value: 'lowest', label: 'Lowest rating' },
    { value: 'alpha-asc', label: 'Alphabetical ↑' },
    { value: 'alpha-desc', label: 'Alphabetical ↓' }
  ]

  const selectedFilter = computed<string>({
    get: () => props.modelValue ?? 'most-reviews',
    set: (v: string) => emit('update:modelValue', v)
  })

  // Votes modal state
  const showVotesModal = ref(false)
  const currentVoteSpot = ref<StudySpot | null>(null)
  function openVotes(s: StudySpot) {
    currentVoteSpot.value = s
    showVotesModal.value = true
  }

  function onVotesRequireAuth() {
    showVotesModal.value = false
    promptAuthForBookmark(currentVoteSpot.value?.id || 0, 'vote')
  }

  // UI for auth prompt
  const showAuthModal = ref(false)
  const attemptedBookmarkId = ref<number | null>(null)
  const authModalTitle = ref('Sign in to save spots')
  const authModalMessage = ref('You need an account to bookmark study spots. Create an account or sign in to save this spot.')

  // Review modal state
  const showReviewModal = ref(false)
  const currentReviewSpot = ref<StudySpot | null>(null)

  function loadUser() {
    try {
      const raw = localStorage.getItem('user')
      currentUser.value = raw ? JSON.parse(raw) : null
    } catch {
      currentUser.value = null
    }
  }

  async function loadBookmarks() {
    if (!currentUser.value?.student_id) {
      bookmarks.value = {}
      return
    }

    try {
      const saved = await fetchSavedSpots(currentUser.value.student_id)
      const map: Record<number, boolean> = {}
      saved.forEach((s: any) => {
        const id = Number(s?.spot_id ?? s?.id)
        if (id) map[id] = true
      })
      bookmarks.value = map
    } catch (err) {
      console.error('Failed to load bookmarks:', err)
      bookmarks.value = {}
    }
  }

  function promptAuthForBookmark(id: number, reason: 'bookmark' | 'report' | 'vote' = 'bookmark') {
    attemptedBookmarkId.value = id
    authModalTitle.value = 'Account Needed'
    if (reason === 'report') {
      authModalMessage.value = 'You need an account to write a review about study spots. Create an account or sign in to continue.'
    } else if (reason === 'vote') {
      authModalMessage.value = 'You need an account to vote on study spots. Create an account or sign in to cast a vote.'
    } else {
      authModalMessage.value = 'You need an account to bookmark study spots. Create an account or sign in to save this spot.'
    }
    showAuthModal.value = true
  }

  function closeAuthOverlay() {
    attemptedBookmarkId.value = null
    showAuthModal.value = false
  }

  function goToAccount() {
    closeAuthOverlay()
    router.push('/account')
  }

  async function toggleBookmark(id: number) {
    if (!currentUser.value?.student_id) {
      promptAuthForBookmark(id, 'bookmark')
      return
    }

    const desired = !bookmarks.value[id]
    bookmarks.value[id] = desired
    try {
      if (desired) await saveSpot(currentUser.value.student_id, id)
      else await unsaveSpot(currentUser.value.student_id, id)

      window.dispatchEvent(new CustomEvent('bookmarks-changed', { detail: { id, bookmarked: desired } }))
    } catch (error) {
      console.error('Failed to update bookmark:', error)
      bookmarks.value[id] = !desired
    }
  }

  function handleReport(spot: StudySpot) {
    if (!currentUser.value?.student_id) {
      promptAuthForBookmark(spot.id, 'report')
      return
    }

    currentReviewSpot.value = spot
    showReviewModal.value = true
  }

  function closeReviewModal() {
    currentReviewSpot.value = null
    showReviewModal.value = false
  }

  async function onReviewSubmitted(review: any) {
    if (!currentUser.value?.student_id) return
    try {
      const created = await addReview({
        student_id: currentUser.value.student_id,
        spot_id: review.spot_id,
        rating: review.rating,
        text: review.text
      })
      window.dispatchEvent(new CustomEvent('reviews-changed', { detail: { spotId: created.spot_id, review: created } }))
    } catch (error) {
      console.error('Failed to submit review:', error)
    }
  }

  function syncBookmarksFromEvent() {
    loadBookmarks()
  }

  onMounted(() => {
    try {
      props.spots.forEach(s => {
        if (s && s.id != null) addOrUpdateSpot(s)
      })
    } catch {
    }

    loadUser()
    loadBookmarks()
    primeReviewsForSpots(props.spots.map(s => s.id)).catch(() => {})
    window.addEventListener('bookmarks-changed', syncBookmarksFromEvent)
    window.addEventListener('reviews-changed', onReviewsChanged)

    // Close auth overlay if account state changes
    const onAccountChanged = (e: Event) => {
      const detail = (e as CustomEvent).detail
      if (detail) {
        closeAuthOverlay()
        loadUser()
        loadBookmarks()
      } else {
        currentUser.value = null
        bookmarks.value = {}
      }
    }
    window.addEventListener('account-changed', onAccountChanged)

      ; (window as any).__studyspotlist_onAccountChanged = onAccountChanged
  })

  watch(() => props.spots, (newSpots) => {
    primeReviewsForSpots(newSpots.map(s => s.id)).catch(() => {})
  })

  onBeforeUnmount(() => {
    window.removeEventListener('bookmarks-changed', syncBookmarksFromEvent)
    window.removeEventListener('reviews-changed', onReviewsChanged)
    const onAccountChanged = (window as any).__studyspotlist_onAccountChanged
    if (onAccountChanged) window.removeEventListener('account-changed', onAccountChanged)
  })

  function combinedRating(spot: StudySpot) {
    if (!spot) return 0
    const baseRating = Number((spot as any).rating ?? (spot as any).avg_rating ?? 0)
    if (!Number.isNaN(baseRating) && baseRating > 0) return Number(baseRating.toFixed(2))

    const reviews = getReviewsForSpot(spot.id)
    if (!reviews || reviews.length === 0) return 0
    const sum = reviews.reduce((s, r) => s + (r.rating || 0), 0)
    const total = reviews.length
    return Number((sum / total).toFixed(2))
  }

  function formatRating(value: number | null | undefined) {
    if (value == null || Number.isNaN(Number(value))) return '0.00'
    return Number(value).toFixed(2)
  }

  const sortedSpots = computed(() => {
    const arr = [...(props.spots || [])]

    function reviewsCount(s: StudySpot) {
      const r = getReviewsForSpot(s.id)
      return (r && r.length) || 0
    }

    switch (selectedFilter.value) {
      case 'least-reviews':
        return arr.sort((a, b) => reviewsCount(a) - reviewsCount(b))
      case 'highest':
        return arr.sort((a, b) => Number(combinedRating(b)) - Number(combinedRating(a)))
      case 'lowest':
        return arr.sort((a, b) => Number(combinedRating(a)) - Number(combinedRating(b)))
      case 'alpha-asc':
        return arr.sort((a, b) => (a.name || '').toLowerCase().localeCompare((b.name || '').toLowerCase()))
      case 'alpha-desc':
        return arr.sort((a, b) => (b.name || '').toLowerCase().localeCompare((a.name || '').toLowerCase()))
      case 'most-reviews':
      default:
        return arr.sort((a, b) => reviewsCount(b) - reviewsCount(a))
    }
  })

  function onReviewsChanged(e: Event) {
    const detail = (e as CustomEvent).detail
    if (detail?.spotId) fetchReviewsForSpot(Number(detail.spotId)).catch(() => {})
  }
</script>
