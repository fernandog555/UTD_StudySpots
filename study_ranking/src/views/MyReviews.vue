<template>
  <div class="p-6">
    <div class="flex items-center justify-between mb-4">
      <h1 class="text-3xl">My Reviews</h1>

      <div>
        <Filter v-model="selectedFilter"
                :options="[
            { value: 'newest', label: 'Newest' },
            { value: 'oldest', label: 'Oldest' },
            { value: 'highest', label: 'Highest rating' },
            { value: 'lowest', label: 'Lowest rating' },
            { value: 'alpha-asc', label: 'Alphabetical ↑' },
            { value: 'alpha-desc', label: 'Alphabetical ↓' }
          ]"
                id="review-filter"
                label="Filter reviews" />
      </div>
    </div>

    <div v-if="requiresLogin" class="p-4 border rounded bg-(--bg_highlight) text-(--dark5)">
      <p>Please sign in to view your reviews.</p>
    </div>

    <div v-else>
      <div v-if="displayedReviews.length === 0" class="p-4 border rounded bg-(--bg_highlight) text-(--dark5)">
        <p>No reviews found for <strong>{{ username }}</strong>.</p>
      </div>

      <ul v-else class="space-y-4">
        <li v-for="r in displayedReviews" :key="r.id" class="p-4 border rounded bg-(--bg_highlight)">
          <div class="flex justify-between items-start">
            <div>
              <p class="font-semibold">
                {{ spotName(r.spot_id) }}
              </p>
              <p class="text-sm text-(--dark5)">{{ r.date }}</p>
            </div>

            <div class="text-yellow-500 font-bold">{{ formatRating(r.rating) }} / 5</div>
          </div>

          <p class="mt-2 text-(--dark5)">{{ r.text }}</p>
          <p class="mt-2 text-xs text-(--dark5)">Author: {{ r.author }}</p>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
  import { fetchUserReviews } from '@/data/reviewsMap'
  import type Review from '@/classes/reviews'
  import Filter from '@/components/Filter.vue'
  import { fetchAndStoreSpots } from '@/data/spotsMap'

  const username = ref<string | null>(localStorage.getItem('username'))
  const studentId = ref<number | null>(null)

  const userReviews = ref<Review[]>([])
  const spotsById = ref<Record<number, any>>({})

  const selectedFilter = ref<string>('newest')

  const requiresLogin = computed(() => !studentId.value)

  async function loadStudySpots() {
    try {
      const arr = await fetchAndStoreSpots()
      const map: Record<number, any> = {}
      arr.forEach((s: any) => {
        if (s && s.id != null) map[s.id] = s
      })
      spotsById.value = map
    } catch {
      spotsById.value = {}
    }
  }

  function loadUser() {
    try {
      const raw = localStorage.getItem('user')
      if (raw) {
        const parsed = JSON.parse(raw)
        username.value = parsed?.netid || parsed?.username || null
        studentId.value = parsed?.student_id ?? null
        return
      }
    } catch {
      // ignore
    }
    username.value = localStorage.getItem('username')
    studentId.value = null
  }

  async function collectUserReviews() {
    if (!studentId.value) {
      userReviews.value = []
      return
    }

    const reviews = await fetchUserReviews(studentId.value)
    userReviews.value = reviews.sort((a, b) => (b.date || '').localeCompare(a.date || ''))
  }

  function spotName(spotId: number): string {
    const s = spotsById.value[spotId]
    return s?.name || 'Unknown Spot'
  }

  function formatRating(r: number | undefined): string {
    if (r == null) return '0.0'
    return r.toFixed(1)
  }

  const displayedReviews = computed(() => {
    const arr = [...userReviews.value]

    switch (selectedFilter.value) {
      case 'newest':
        return arr.sort((a, b) => (b.date || '').localeCompare(a.date || ''))
      case 'oldest':
        return arr.sort((a, b) => (a.date || '').localeCompare(b.date || ''))
      case 'highest':
        return arr.sort((a, b) => (b.rating ?? 0) - (a.rating ?? 0))
      case 'lowest':
        return arr.sort((a, b) => (a.rating ?? 0) - (b.rating ?? 0))
      case 'alpha-asc':
        return arr.sort((a, b) => {
          const nameA = spotName(a.spot_id)
          const nameB = spotName(b.spot_id)
          return nameA.localeCompare(nameB)
        })
      case 'alpha-desc':
        return arr.sort((a, b) => {
          const nameA = spotName(a.spot_id)
          const nameB = spotName(b.spot_id)
          return nameB.localeCompare(nameA)
        })
      default:
        return arr
    }
  })

  async function reloadData() {
    await loadStudySpots()
    await collectUserReviews()
  }

  const onAccountChanged = () => {
    loadUser()
    reloadData()
  }

  onMounted(() => {
    loadUser()
    reloadData()
    // Listen for spots-changed event to reload when spots are deleted
    window.addEventListener('spots-changed', reloadData)
    window.addEventListener('account-changed', onAccountChanged)
  })

  onBeforeUnmount(() => {
    window.removeEventListener('spots-changed', reloadData)
    window.removeEventListener('account-changed', onAccountChanged)
  })
</script>
