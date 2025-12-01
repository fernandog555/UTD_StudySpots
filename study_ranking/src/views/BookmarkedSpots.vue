<template>
  <div class="p-6 relative">
    <div class="flex items-center justify-between mb-4">
      <h1 class="text-3xl mb-0">Bookmarked Spots</h1>

      <Filter v-model="selectedFilter"
              :options="filterOptions"
              id="bookmarked-spot-filter"
              label="Filter study spots" />
    </div>

    <!-- Main content -->
    <div>
      <div v-if="isLoading" class="text-gray-500">Loading bookmarked spots…</div>
      <div v-else-if="loadError" class="text-red-500">{{ loadError }}</div>
      <template v-else>
        <StudySpotList :spots="bookmarkedSpots"
                       v-model="selectedFilter"
                       :show-header="false"
                       @view-details="openDetails"
                       @view-reviews="openDetailsAndReviews" />
        <div v-if="bookmarkedSpots.length === 0" class="mt-4 text-gray-500">
          <p>No bookmarked study spots.</p>
        </div>
      </template>
    </div>

    <div v-if="showModal"
         class="fixed inset-0 z-40"
         style="backdrop-filter: blur(2px); -webkit-backdrop-filter: blur(4px);"
         @click="closeModal"></div>

    <!-- Overlay details modal -->
    <StudySpotDetails v-if="showModal && selectedSpot"
                      :spot="selectedSpot"
                      :initial-open-reviews="reviewsInitialOpen"
                      @close="closeModal" />
  </div>
</template>

<script setup lang="ts">
  import { ref, onMounted, onBeforeUnmount } from 'vue'
  import StudySpot from '../classes/spot.ts'
  import StudySpotList from '@/components/StudySpotList.vue'
  import StudySpotDetails from '@/components/StudySpotDetails.vue'
  import Filter from '@/components/Filter.vue'
  import { mapApiSpot } from '@/data/spotsMap'
  import { fetchSavedSpots, apiGet } from '@/api'

  const bookmarkedSpots = ref<StudySpot[]>([])
  const selectedSpot = ref<StudySpot | null>(null)
  const showModal = ref(false)
  const isLoading = ref(false)
  const loadError = ref('')
  const currentUser = ref<{ student_id: number } | null>(null)

  const reviewsInitialOpen = ref(false)

  const selectedFilter = ref<string>('highest')
  const filterOptions = [
    { value: 'highest', label: 'Highest rating' },
    { value: 'lowest', label: 'Lowest rating' },
    { value: 'most-reviews', label: 'Most reviews' },
    { value: 'least-reviews', label: 'Least reviews' },
    { value: 'alpha-asc', label: 'Alphabetical ↑' },
    { value: 'alpha-desc', label: 'Alphabetical ↓' }
  ]

  function loadUser() {
    try {
      const raw = localStorage.getItem('user')
      currentUser.value = raw ? JSON.parse(raw) : null
    } catch {
      currentUser.value = null
    }
  }


  async function attachRatings(spots: StudySpot[]) {
    await Promise.all(spots.map(async (spot) => {
      try {
        const data = await apiGet(`/ratings/spot/${spot.id}`)
        if (Array.isArray(data) && data.length > 0) {
          const sum = data.reduce((s, r) => s + Number(r.avg_rating ?? 0), 0)
          const avg = sum / data.length
          spot.rating = Number(avg.toFixed(2))
        }
      } catch (err) {
        console.warn('Unable to load ratings for spot', spot.id, err)
      }
    }))}

  async function loadBookmarkedSpots() {
    isLoading.value = true
    loadError.value = ''

    if (!currentUser.value?.student_id) {
      loadError.value = 'Sign in to see your bookmarked study spots.'
      bookmarkedSpots.value = []
      isLoading.value = false
      return
    }

    try {
      const saved = await fetchSavedSpots(currentUser.value.student_id)
      const spots = Array.isArray(saved)
        ? saved.map((s: any) => mapApiSpot({ ...s, spot_id: s.spot_id ?? s.id }))
        : []
        await attachRatings(spots);
        bookmarkedSpots.value = spots;
    } catch (err) {
      console.error('Failed to load bookmarked spots:', err)
      loadError.value = 'Unable to load bookmarked spots.'
      bookmarkedSpots.value = []
    } finally {
      isLoading.value = false
    }
  }

  function openDetails(spot: StudySpot) {
    selectedSpot.value = spot
    reviewsInitialOpen.value = false
    showModal.value = true
  }

  // open details
  function openDetailsAndReviews(spot: StudySpot) {
    selectedSpot.value = spot
    reviewsInitialOpen.value = true
    showModal.value = true
  }

  function closeModal() {
    showModal.value = false
    selectedSpot.value = null
    reviewsInitialOpen.value = false
  }

  function handleAccountChanged() {
    loadUser()
    loadBookmarkedSpots()
  }

  onMounted(() => {
    loadUser()
    loadBookmarkedSpots()
    window.addEventListener('spots-changed', loadBookmarkedSpots)
    window.addEventListener('account-changed', handleAccountChanged)
  })

  onBeforeUnmount(() => {
    window.removeEventListener('spots-changed', loadBookmarkedSpots)
    window.removeEventListener('account-changed', handleAccountChanged)
  })
</script>
