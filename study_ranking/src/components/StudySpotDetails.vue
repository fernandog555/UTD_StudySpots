<template>
  <!-- backdrop -->
  <div class="w-full h-full bg-black/30 z-50 inset-0 fixed flex justify-center items-center backdrop-blur-custom p-2 sm:p-4" @click.self="$emit('close')">
    <!-- Flex container for side-by-side layout -->
    <div :class="showReviewsOverlay ? 'flex flex-row gap-2 lg:gap-4 items-start justify-center overflow-auto max-w-full' : 'flex justify-center'">
      <div ref="detailsRoot"
           :class="['relative bg-(--bg) shadow-lg rounded-lg flex-none']"
           :style="detailsStyle"
           @click.stop>

        <!-- Fixed header with action buttons -->
        <div ref="headerRef" class="flex-none bg-(--bg) z-10 pb-2 border-b border-(--dark3) px-4 sm:px-6 pt-2">
          <!-- Action buttons - Responsive positioning -->
          <div class="absolute top-2 sm:top-4 right-2 sm:right-4 flex gap-1 sm:gap-2">
            <!-- review button -->
            <button v-if="spot"
                    title="Review"
                    @click="handleReport"
                    class="w-8 h-8 sm:w-9 sm:h-9 flex items-center justify-center rounded-md hover:bg-black/10 transition"
                    aria-label="Review this spot">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
                   class="w-4 h-4 sm:w-5 sm:h-5 text-(--dark5)" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 20h9" />
                <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 3.5a2.121 2.121 0 1 1 3 3L8 18l-4 1 1-4 11.5-11.5z" />
              </svg>
            </button>

            <!-- bookmark button -->
            <button v-if="spot"
                    @click="toggleBookmark"
                    :aria-pressed="isBookmarked"
                    :title="isBookmarked ? 'Remove bookmark' : 'Add bookmark'"
                    class="w-8 h-8 sm:w-9 sm:h-9 flex items-center justify-center rounded-md hover:bg-black/10 transition">
              <svg v-if="isBookmarked" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
                   class="w-4 h-4 sm:w-5 sm:h-5 text-yellow-400 fill-current" aria-hidden="true">
                <path d="M6 2a1 1 0 0 0-1 1v18l7-4 7 4V3a1 1 0 0 0-1-1H6z" />
              </svg>

              <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
                   class="w-4 h-4 sm:w-5 sm:h-5 text-yellow-400" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 2a1 1 0 0 0-1 1v18l7-4 7 4V3a1 1 0 0 0-1-1H6z" />
              </svg>
            </button>

            <!-- close button -->
            <button class="w-8 h-8 sm:w-9 sm:h-9 text-lg sm:text-xl font-bold cursor-pointer hover:text-red-500 flex items-center justify-center" @click="$emit('close')">
              ✕
            </button>
          </div>

          <h1 class="text-xl sm:text-2xl md:text-3xl mb-3 sm:mb-4 pr-20 sm:pr-24 break-words">{{ spot?.name }}</h1>
        </div>

        <!-- Scrollable content area -->
        <div class="flex-1 overflow-y-auto px-4 sm:px-6 py-4" :style="scrollAreaStyle">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3 sm:gap-4 md:gap-6">
            <!-- Location Section -->
            <div class="bg-(--bg_highlight) p-3 sm:p-4 rounded-md border">
              <h2 class="text-lg sm:text-xl font-semibold mb-2">Location</h2>
              <p class="text-sm sm:text-base break-words"><strong>Building:</strong> {{ spot?.building_code }}</p>
              <p class="text-sm sm:text-base break-words"><strong>Area:</strong> {{ spot?.area_description }}</p>
            </div>

            <!-- Environment Section -->
            <div class="bg-(--bg_highlight) p-3 sm:p-4 rounded-md border">
              <h2 class="text-lg sm:text-xl font-semibold mb-2">Environment</h2>
              <p class="text-sm sm:text-base"><strong>Seating Capacity:</strong> {{ spot?.seating_capacity }}</p>
              <p class="text-sm sm:text-base"><strong>Power Outlets:</strong> {{ spot?.power_outlets ? 'Yes' : 'No' }}</p>
              <p class="text-sm sm:text-base"><strong>Natural Light:</strong> {{ spot?.natural_light ? 'Yes' : 'No' }}</p>
              <p class="text-sm sm:text-base"><strong>Open 24/7:</strong> {{ spot?.open_24_7 ? 'Yes' : 'No' }}</p>
            </div>

            <!-- Rating Section -->
            <div class="bg-(--bg_highlight) p-3 sm:p-4 rounded-md border md:col-span-2 space-y-3">
              <h2 class="text-lg sm:text-xl font-semibold">Ratings</h2>
              <div v-if="isLoadingRatings" class="text-(--dark5)">Loading ratings…</div>
              <div v-else-if="ratingError" class="text-red-500 text-sm">{{ ratingError }}</div>
              <template v-else>
                <p class="text-xl sm:text-2xl font-bold text-yellow-500">{{ formatRating(combinedRatingForSpot) }} / 5</p>
                <div v-if="categoryAverages.length" class="grid grid-cols-1 sm:grid-cols-2 gap-2 sm:gap-3">
                  <div v-for="cat in categoryAverages"
                       :key="cat.category_id"
                       class="p-3 rounded-md border bg-black/20">
                    <p class="font-semibold">{{ cat.display_name }}</p>
                    <p class="text-yellow-500 text-lg">{{ formatRating(cat.avg_rating) }} / 5</p>
                    <p class="text-xs text-(--dark5)">{{ cat.vote_count }} vote(s)</p>
                  </div>
                </div>
                <p v-else class="text-(--dark5)">No ratings yet. Be the first to vote!</p>
              </template>
            </div>

            <!-- Description Section -->
            <div class="bg-(--bg_highlight) p-3 sm:p-4 rounded-md border md:col-span-2">
              <h2 class="text-lg sm:text-xl font-semibold mb-2">Description</h2>
              <p class="text-(--dark5) text-sm sm:text-base break-words whitespace-pre-wrap">{{ spot?.description }}</p>
            </div>

            <!-- Metadata Section -->
            <div class="bg-(--bg_highlight) p-3 sm:p-4 rounded-md border">
              <h2 class="text-lg sm:text-xl font-semibold mb-2">Metadata</h2>
              <p class="text-sm sm:text-base"><strong>ID:</strong> {{ spot?.id }}</p>
              <p class="text-sm sm:text-base"><strong>Creator ID:</strong> {{ spot?.creator_id }}</p>
              <p class="text-sm sm:text-base"><strong>Active:</strong> {{ spot?.is_active ? 'Yes' : 'No' }}</p>
            </div>

            <!-- Categories Section -->
            <div class="bg-(--bg_highlight) p-3 sm:p-4 rounded-md border">
              <h2 class="text-lg sm:text-xl font-semibold mb-2">Categories</h2>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 sm:gap-4">
                <ul v-for="category in spot?.categories" :key="category" class="rounded-md border flex items-center
                      justify-center bg-black/25 hover:bg-black/50 hover:cursor-pointer text-sm sm:text-base py-2 break-words">
                  <li>
                    {{ category }}
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Reviews side-by-side panel -->
      <div v-if="showReviewsOverlay" class="flex-none" @click.stop>
        <StudySpotReviews :spot="spot" variant="panel" @close="closeReviews" />
      </div>
    </div>

    <!-- Votes modal -->
    <Votes v-model:visible="showVotesModal" :spot="spot" @require-auth="onVotesRequireAuth" />

    <!-- Reusable Auth modal -->
    <Auth v-model="showAuthOverlay"
          :title="authModalTitle"
          :message="authModalMessage"
          @confirm="goToAccount"
          @cancel="onAuthCancel" />

    <Review v-if="showReviewModal" :spot="currentReviewSpot" @close="closeReviewModal" @submitted="onReviewSubmitted" />
  </div>
</template>

<script setup lang="ts">
  import { onMounted, onBeforeUnmount, ref, watch, computed, nextTick } from 'vue'
  import { useRouter } from 'vue-router'
  import StudySpot from '../classes/spot.ts'
  import StudySpotReviews from './StudySpotReviews.vue'
  import { addReview, fetchReviewsForSpot } from '../data/reviewsMap'
  import Auth from '../views/Auth.vue'
  import Review from './Review.vue'
  import Votes from './Votes.vue'
  import { useSyncedHeaderHeight } from '../composables/useSyncedHeaderHeight'
  import { apiGet } from '../api'
  import { fetchSavedSpots, saveSpot, unsaveSpot } from '@/api'

  const props = defineProps<{
    spot: StudySpot | null,
    initialOpenReviews?: boolean
  }>()

  const emit = defineEmits<{
    (e: 'close'): void
    (e: 'view-reviews', spot: StudySpot): void
    (e: 'report-spot', spot: StudySpot): void
  }>()

  const router = useRouter()
  const isBookmarked = ref(false)
  const currentUser = ref<{ student_id: number; netid?: string } | null>(null)
  const savedIds = ref<Set<number>>(new Set())

  // UI for auth prompt
  const showAuthOverlay = ref(false)
  const attemptedBookmarkId = ref<number | null>(null)
  const authModalTitle = ref('Account Needed')
  const authModalMessage = ref('You need an account to bookmark study spots. Create an account or sign in to save this spot.')

  // reviews overlay
  const showReviewsOverlay = ref(false)

  const showReviewModal = ref(false)
  const currentReviewSpot = ref<StudySpot | null>(null)

  // votes modal
  const showVotesModal = ref(false)
  const categoryAverages = ref<Array<{ category_id: number; display_name: string; avg_rating: number; vote_count: number }>>([])
  const isLoadingRatings = ref(false)
  const ratingError = ref('')

  // Fixed single dimension values - SAME SIZE ALWAYS
  const detailsRoot = ref<HTMLElement | null>(null)

  // Use synced header height composable
  const { headerRef } = useSyncedHeaderHeight()

  const detailsStyle = computed(() => {
    // Allow scaling down to minimum size on smaller screens
    // No viewport-based middle value - goes straight to min size when needed
    return {
      width: 'min(600px, 100vw - 1rem)',
      minWidth: '360px',
      maxWidth: '600px',
      height: 'min(700px, 100vh - 1rem)',
      minHeight: '420px',
      maxHeight: '700px',
      display: 'flex',
      flexDirection: 'column',
      boxSizing: 'border-box',
      padding: '0',
      flex: '0 0 auto',
      overflow: 'hidden'
    }
  })

  const scrollAreaStyle = computed(() => {
    // Let flexbox handle the height with flex-1
    return {
      minHeight: '0' // Critical for flexbox scroll containers
    }
  })

  function loadUser() {
    try {
      const raw = localStorage.getItem('user')
      currentUser.value = raw ? JSON.parse(raw) : null
    } catch {
      currentUser.value = null
    }
  }

  async function loadSavedSpots() {
    if (!currentUser.value?.student_id) {
      savedIds.value = new Set()
      isBookmarked.value = false
      return
    }

    try {
      const saved = await fetchSavedSpots(currentUser.value.student_id)
      const set = new Set<number>()
      saved.forEach((s: any) => {
        const id = Number(s?.spot_id ?? s?.id)
        if (id) set.add(id)
      })
      savedIds.value = set
      loadBookmarkForCurrentSpot()
    } catch (err) {
      console.error('Failed to load saved spots:', err)
      savedIds.value = new Set()
      isBookmarked.value = false
    }
  }

  function loadBookmarkForCurrentSpot() {
    if (!props.spot) {
      isBookmarked.value = false
      return
    }
    isBookmarked.value = savedIds.value.has(props.spot.id)
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
    showAuthOverlay.value = true
  }

  function closeAuthOverlay() {
    attemptedBookmarkId.value = null
    showAuthOverlay.value = false
  }

  function goToAccount() {
    closeAuthOverlay()
    router.push('/account')
  }

  async function toggleBookmark() {
    if (!props.spot) return
    if (!currentUser.value?.student_id) {
      promptAuthForBookmark(props.spot.id, 'bookmark')
      return
    }

    const desired = !isBookmarked.value
    isBookmarked.value = desired
    try {
      if (desired) await saveSpot(currentUser.value.student_id, props.spot.id)
      else await unsaveSpot(currentUser.value.student_id, props.spot.id)

      if (desired) savedIds.value.add(props.spot.id)
      else savedIds.value.delete(props.spot.id)

      window.dispatchEvent(new CustomEvent('bookmarks-changed', { detail: { id: props.spot.id, bookmarked: desired } }))
    } catch (error) {
      console.error('Failed to toggle bookmark:', error)
      isBookmarked.value = !desired
    }
  }

  function handleReport() {
    if (!props.spot) return
    if (!currentUser.value?.student_id) {
      promptAuthForBookmark(props.spot.id, 'report')
      return
    }

    currentReviewSpot.value = props.spot
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

  function onAuthCancel() {
    closeAuthOverlay()
  }

  // Toggle reviews overlay
  async function toggleReviews() {
    if (!props.spot) return
    showReviewsOverlay.value = !showReviewsOverlay.value
    if (showReviewsOverlay.value) {
      emit('view-reviews', props.spot)
      await nextTick()
      // Notify the reviews component to update its size
      window.dispatchEvent(new Event('resize'))
    }
  }

  function closeReviews() {
    showReviewsOverlay.value = false
  }

  function openVotes() {
    if (!props.spot) return
    showVotesModal.value = true
  }

  function onVotesRequireAuth() {
    if (!props.spot) return
    showVotesModal.value = false
    promptAuthForBookmark(props.spot?.id, 'vote')
  }

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Escape') {
      if (showAuthOverlay.value) {
        closeAuthOverlay()
        return
      }

      if (showVotesModal.value) {
        showVotesModal.value = false
        return
      }

      if (showReviewsOverlay.value) {
        closeReviews()
        return
      }

      // close review modal if open
      if (showReviewModal.value) {
        closeReviewModal()
        return
      }

      emit('close')
    }
  }

  function syncFromExternalChange(e: Event) {
    loadUser()
    loadSavedSpots()
    loadBookmarkForCurrentSpot()
    if (props.spot?.id) fetchReviewsForSpot(props.spot.id).catch(() => {})
  }

  async function loadRatings() {
    if (!props.spot) {
      categoryAverages.value = []
      return
    }

    isLoadingRatings.value = true
    ratingError.value = ''
    try {
      const data = await apiGet(`/ratings/spot/${props.spot.id}`)
      categoryAverages.value = Array.isArray(data) ? data : []
    } catch (err) {
      console.error('Failed to load ratings:', err)
      ratingError.value = 'Unable to load ratings for this spot.'
      categoryAverages.value = []
    } finally {
      isLoadingRatings.value = false
    }
  }

  onMounted(() => {
    window.addEventListener('keydown', handleKeyDown)
    window.addEventListener('bookmarks-changed', syncFromExternalChange)
    loadUser()
    loadSavedSpots()
    loadBookmarkForCurrentSpot()
    loadRatings()

    if (props.initialOpenReviews) {
      showReviewsOverlay.value = true
      if (props.spot) emit('view-reviews', props.spot)
    }

    const onAccountChanged = (e: Event) => {
      const detail = (e as CustomEvent).detail
      if (detail) {
        closeAuthOverlay()
        closeReviewModal()
        loadUser()
        loadSavedSpots()
      } else {
        currentUser.value = null
        savedIds.value = new Set()
        isBookmarked.value = false
      }
    }
    window.addEventListener('account-changed', onAccountChanged)
      ; (window as any).__studyspotdetails_onAccountChanged = onAccountChanged

    const onRatingsUpdated = (e: Event) => {
      const detail = (e as CustomEvent).detail
      if (props.spot && detail?.spotId === props.spot.id) {
        loadRatings()
      }
    }
    window.addEventListener('ratings-updated', onRatingsUpdated)
      ; (window as any).__studyspotdetails_onRatingsUpdated = onRatingsUpdated
  })

  onBeforeUnmount(() => {
    window.removeEventListener('keydown', handleKeyDown)
    window.removeEventListener('bookmarks-changed', syncFromExternalChange)

    const onAccountChanged = (window as any).__studyspotdetails_onAccountChanged
    if (onAccountChanged) window.removeEventListener('account-changed', onAccountChanged)

    const onRatingsUpdated = (window as any).__studyspotdetails_onRatingsUpdated
    if (onRatingsUpdated) window.removeEventListener('ratings-updated', onRatingsUpdated)
  })

  watch(() => props.spot, () => {
    loadUser()
    loadSavedSpots()
    loadBookmarkForCurrentSpot()
    loadRatings()
    if (props.spot?.id) fetchReviewsForSpot(props.spot.id).catch(() => {})
  })

  const combinedRatingForSpot = computed(() => {
    if (categoryAverages.value.length > 0) {
      const sum = categoryAverages.value.reduce((s, r) => s + Number(r.avg_rating ?? 0), 0)
      return Number((sum / categoryAverages.value.length).toFixed(2))
    }

    const spot = props.spot
    if (spot && spot.rating) return Number(spot.rating.toFixed(2))
    return 0
  })

  function formatRating(value: number | null | undefined) {
    if (value == null || Number.isNaN(Number(value))) return '0.00'
    return Number(value).toFixed(2)
  }
</script>
