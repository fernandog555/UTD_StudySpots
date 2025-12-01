<template>
  <div class="p-4 sm:p-6 lg:p-8 relative">
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-4 gap-3 sm:gap-4">
      <h1 class="text-2xl sm:text-3xl mb-0">Search Results for {{ displayQuery }}</h1>

      <Filter v-model="selectedFilter"
              :options="filterOptions"
              id="search-spot-filter"
              label="Filter study spots" />
    </div>

    <!-- Main content -->
    <div>
      <div v-if="isLoading" class="text-gray-500">Loading study spots…</div>
      <div v-else-if="loadError" class="text-red-500">{{ loadError }}</div>
      <template v-else>
        <StudySpotList :spots="filteredSpots"
                       v-model="selectedFilter"
                       :show-header="false"
                       @view-details="openDetails"
                       @view-reviews="openDetailsAndReviews" />
        <div v-if="filteredSpots.length === 0" class="mt-4 text-gray-500 text-center sm:text-left">
          <p>No study spots found.</p>
        </div>
      </template>
    </div>

    <!-- Overlay details modal -->
    <StudySpotDetails v-if="showModal && selectedSpot"
                      :spot="selectedSpot"
                      :initial-open-reviews="reviewsInitialOpen"
                      @close="closeModal" />
  </div>
</template>

<script setup lang="ts">
  import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
  import { useRoute } from 'vue-router'
  import StudySpot from '../classes/spot.ts'
  import StudySpotList from '@/components/StudySpotList.vue'
  import StudySpotDetails from '@/components/StudySpotDetails.vue'
  import { fetchAndStoreSpots } from '../data/spotsMap'
  import Filter from '@/components/Filter.vue'
  import { apiGet } from '../api'

  const route = useRoute()
  const query = ref((route.params.query as string) || '')

  watch(() => route.params.query, (newQuery) => {
    query.value = (newQuery as string) || ''
  })

  const allSpots = ref<StudySpot[]>([])
  const isLoading = ref(false)
  const loadError = ref('')

  const filteredSpots = computed(() =>
    allSpots.value.filter(spot =>
      spot.name.toLowerCase().includes(query.value.toLowerCase())
    )
  )

  const displayQuery = computed(() => query.value || 'All Spots')

  const selectedFilter = ref<string>('highest')
  const filterOptions = [
    { value: 'highest', label: 'Highest rating' },
    { value: 'lowest', label: 'Lowest rating' },
    { value: 'most-reviews', label: 'Most reviews' },
    { value: 'least-reviews', label: 'Least reviews' },
    { value: 'alpha-asc', label: 'Alphabetical ↑' },
    { value: 'alpha-desc', label: 'Alphabetical ↓' }
  ]

  // Modal state
  const selectedSpot = ref<StudySpot | null>(null)
  const showModal = ref(false)
  const reviewsInitialOpen = ref(false)

  function openDetails(spot: StudySpot) {
    selectedSpot.value = spot
    reviewsInitialOpen.value = false
    showModal.value = true
  }

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

  async function reloadSpots() {
    isLoading.value = true
    loadError.value = ''
    try {
      const spots = await fetchAndStoreSpots()
      await attachRatings(spots)
      allSpots.value = spots
      localStorage.setItem('studySpots', JSON.stringify(spots))
    } catch (err) {
      console.error('Failed to load spots from backend:', err)
      loadError.value = 'Unable to load study spots right now.'
    } finally {
      isLoading.value = false
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
    }))
  }

  onMounted(() => {
    reloadSpots()
    window.addEventListener('spots-changed', reloadSpots)
  })

  onBeforeUnmount(() => {
    window.removeEventListener('spots-changed', reloadSpots)
  })
</script>
