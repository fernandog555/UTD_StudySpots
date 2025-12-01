<template>
  <div class="space-y-4">
    <div class="bg-[var(--bg_highlight)] p-4 rounded-lg border">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-2xl font-semibold">My Submitted Spots</h2>

        <Filter v-if="spots.length > 0"
                v-model="selectedFilter"
                :options="filterOptions"
                id="spot-filter"
                label="Filter spots" />
      </div>

      <div v-if="spots.length === 0" class="text-[var(--dark5)] text-center py-8">
        <p>You haven't submitted any study spots yet.</p>
        <button @click="$emit('switch-to-submit')"
                class="mt-4 px-4 py-2 text-blue-600 hover:underline">
          Submit your first spot →
        </button>
      </div>

      <div v-else class="space-y-3">
        <div v-for="spot in sortedSpots"
             :key="spot.id"
             class="p-4 border rounded bg-[var(--bg)] hover:bg-[var(--bg_highlight)]/50 transition-colors">
          <div class="flex justify-between items-start">
            <div class="flex-1">
              <h3 class="text-xl font-semibold">{{ spot.name }}</h3>
              <p class="text-sm text-[var(--dark5)] mt-1">{{ spot.building_code }} • {{ spot.description }}</p>
              <div class="flex items-center gap-4 mt-2 text-sm text-[var(--dark5)]">
                <span>⭐ {{ spot.rating.toFixed(1) }}</span>
                <span>💬 {{ getReviewCount(spot.id) }} reviews</span>
                <span v-if="spot.seating_capacity">🪑 {{ spot.seating_capacity }} seats</span>
                <span v-if="spot.power_outlets">🔌 Power</span>
                <span v-if="spot.natural_light">☀️ Natural Light</span>
                <span v-if="spot.open_24_7">🕐 24/7</span>
              </div>
              <div v-if="spot.categories.length" class="flex flex-wrap gap-1 mt-2">
                <span v-for="cat in spot.categories"
                      :key="cat"
                      class="px-6 py-2 rounded-md text-base text-center hover:cursor-pointer hover:bg-(--fg_gutter) border">
                  {{ cat }}
                </span>
              </div>
            </div>
            <div class="flex gap-2 ml-4">
              <button @click="$emit('view-spot', spot)"
                      class="px-6 py-2 rounded-md text-base text-center hover:cursor-pointer hover:bg-(--fg_gutter) border">
                View Details
              </button>
              <button @click="$emit('edit-spot', spot)"
                      class="px-6 py-2 rounded-md text-base text-center hover:cursor-pointer hover:bg-(--fg_gutter) border">
                Edit
              </button>
              <button @click="openDeleteModal(spot)"
                      class="px-6 py-2 rounded-md text-base text-center hover:cursor-pointer hover:bg-(--red1)/10 border text-(--red1) border-(--red1)">
                Delete
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal"
         class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/30 backdrop-blur-custom"
         @click.self="closeDeleteModal">
      <div class="bg-[var(--bg)] rounded-md shadow-xl w-full max-w-md p-6">
        <h2 class="text-2xl font-semibold mb-4">Delete Study Spot</h2>
        <p class="text-[var(--dark5)] mb-6">
          Are you sure you want to delete <strong>{{ spotToDelete?.name }}</strong>? This action cannot be undone.
        </p>
        <div class="flex gap-3 justify-end">
          <button @click="closeDeleteModal"
                  class="px-4 py-2 border rounded hover:bg-[var(--bg_highlight)] transition-colors">
            Cancel
          </button>
          <button @click="confirmDelete"
                  class="px-6 py-2 rounded-md text-base text-center hover:cursor-pointer hover:bg-(--red1)/10 border text-(--red1) border-(--red1)">
            Delete
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ref, computed, watch } from 'vue'
  import type StudySpot from '@/classes/spot'
  import Filter from './Filter.vue'
  import { getReviewsForSpot } from '@/data/reviewsMap'
  import { apiGet } from '../api'

  const props = defineProps<{
    spots: StudySpot[]
  }>()

  const emit = defineEmits<{
    (e: 'edit-spot', spot: StudySpot): void
    (e: 'view-spot', spot: StudySpot): void
    (e: 'delete-spot', spot: StudySpot): void
    (e: 'switch-to-submit'): void
  }>()

  const showDeleteModal = ref(false)
  const spotToDelete = ref<StudySpot | null>(null)
  const selectedFilter = ref('rating-high')

  const filterOptions = [
    { value: 'rating-high', label: 'Highest Rating' },
    { value: 'rating-low', label: 'Lowest Rating' },
    { value: 'reviews-most', label: 'Most Reviews' },
    { value: 'reviews-least', label: 'Least Reviews' },
    { value: 'alpha-asc', label: 'Alphabetical ↑' },
    { value: 'alpha-desc', label: 'Alphabetical ↓' }
  ]

  function getReviewCount(spotId: number): number {
    const reviews = getReviewsForSpot(spotId)
    return reviews.length
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

  const sortedSpots = computed(() => {
    const spotsCopy = [...props.spots]

    switch (selectedFilter.value) {
      case 'rating-high':
        return spotsCopy.sort((a, b) => b.rating - a.rating)

      case 'rating-low':
        return spotsCopy.sort((a, b) => a.rating - b.rating)

      case 'reviews-most':
        return spotsCopy.sort((a, b) => {
          const aCount = getReviewCount(a.id)
          const bCount = getReviewCount(b.id)
          return bCount - aCount
        })

      case 'reviews-least':
        return spotsCopy.sort((a, b) => {
          const aCount = getReviewCount(a.id)
          const bCount = getReviewCount(b.id)
          return aCount - bCount
        })

      case 'alpha-asc':
        return spotsCopy.sort((a, b) => a.name.localeCompare(b.name))

      case 'alpha-desc':
        return spotsCopy.sort((a, b) => b.name.localeCompare(a.name))

      default:
        return spotsCopy
    }
  })

  function openDeleteModal(spot: StudySpot) {
    spotToDelete.value = spot
    showDeleteModal.value = true
  }

  function closeDeleteModal() {
    showDeleteModal.value = false
    spotToDelete.value = null
  }

  function confirmDelete() {
    if (spotToDelete.value) {
      emit('delete-spot', spotToDelete.value)
      closeDeleteModal()
    }
  }

  watch(() => props.spots, (newSpots) => {
    if(newSpots && newSpots.length > 0){
      attachRatings(newSpots)
    }
  }, { immediate: true })
</script>
