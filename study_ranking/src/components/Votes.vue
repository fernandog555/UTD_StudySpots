<template>
  <div v-if="visible" class="fixed inset-0 z-60 flex items-center justify-center p-2 sm:p-4 bg-black/50 backdrop-blur-custom" @click.self="close">
    <div class="relative w-full max-w-2xl max-h-[90vh] flex flex-col">
      <div class="z-50 w-full mx-auto rounded-xl bg-[var(--bg)] border shadow-xl flex flex-col overflow-hidden"
           role="dialog"
           aria-modal="true"
           @click.stop>
        <div class="relative p-4 sm:p-6 md:p-8 pb-3 sm:pb-4 border-b flex-shrink-0">
          <button class="absolute top-3 sm:top-5 right-3 sm:right-5 text-xl sm:text-2xl font-bold cursor-pointer hover:text-red-500 transition-colors duration-150 z-10 p-1 sm:p-2"
                  @click="close"
                  aria-label="Close votes modal">
            ✕
          </button>

          <div class="mb-3 sm:mb-4">
            <h3 class="text-2xl sm:text-3xl font-semibold pr-10 sm:pr-14 break-words">Rate {{ spot?.name }}</h3>
          </div>

          <p class="text-xs sm:text-sm text-[var(--fg_dark)]">
            Choose a category and submit a 1-5 rating. You can update your rating anytime.
          </p>
          <p v-if="error" class="text-red-500 text-sm mt-2">{{ error }}</p>
          <p v-if="success" class="text-green-500 text-sm mt-2">{{ success }}</p>
        </div>

        <div class="overflow-y-auto flex-1 p-4 sm:p-6 md:p-8 pt-3 sm:pt-4">
          <div v-if="isLoading" class="text-(--fg_dark)">Loading categories…</div>
          <div v-else-if="!categories.length" class="text-(--fg_dark)">No rating categories available.</div>

          <ul v-else class="space-y-3 sm:space-y-4">
            <li v-for="cat in categories" :key="cat.category_id" class="p-3 sm:p-4 border rounded bg-[var(--bg)] space-y-2">
              <div class="flex items-center justify-between gap-3 flex-wrap">
                <div class="flex-1 min-w-[180px]">
                  <div class="font-medium text-sm sm:text-base">{{ cat.display_name }}</div>
                  <div class="text-xs sm:text-sm text-[var(--fg_dark)]">
                    Average: {{ formatRating(categoryStats[cat.category_id]?.avg_rating) }} ({{ categoryStats[cat.category_id]?.vote_count ?? 0 }} votes)
                  </div>
                </div>
                <div class="flex items-center gap-3 flex-1">
                  <input type="range" min="1" max="5" step="1"
                         v-model.number="ratingInputs[cat.category_id]"
                         class="flex-1" />
                  <span class="font-semibold text-yellow-500 min-w-[60px] text-right">{{ ratingInputs[cat.category_id] ?? 3 }} / 5</span>
                </div>
              </div>

              <textarea v-model="commentInputs[cat.category_id]"
                        placeholder="Optional comment"
                        class="w-full mt-1 p-2 rounded border bg-(--bg_highlight) text-sm"></textarea>

              <div class="flex justify-end">
                <button class="px-4 sm:px-6 py-2 sm:py-2.5 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-60"
                        :disabled="isSubmitting"
                        @click="submitRating(cat.category_id)">
                  {{ isSubmitting ? 'Saving…' : 'Submit Rating' }}
                </button>
              </div>
            </li>
          </ul>

          <div class="mt-3 sm:mt-4 flex justify-start">
            <button class="px-4 sm:px-6 py-2 sm:py-3 border rounded hover:bg-[var(--bg_highlight)] text-sm sm:text-base"
                    @click="close">
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ref, watch, computed } from 'vue'
  import type StudySpot from '@/classes/spot'
  import { apiGet, apiPost } from '@/api'
  import { submitVoteToBackend } from '@/data/votesMap'

  type Category = { category_id: number; slug: string; display_name: string }

  const props = defineProps<{
    spot: StudySpot | null
    visible: boolean
  }>()

  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void
    (e: 'require-auth'): void
  }>()

  const categories = ref<Category[]>([])
  const categoryStats = ref<Record<number, { avg_rating: number; vote_count: number }>>({})
  const ratingInputs = ref<Record<number, number>>({})
  const commentInputs = ref<Record<number, string>>({})
  const isLoading = ref(false)
  const isSubmitting = ref(false)
  const error = ref('')
  const success = ref('')
  const userVotes = ref<Record<number, any>>({})

  const user = computed(() => {
    const raw = localStorage.getItem('user')
    if (!raw) return null
    try {
      return JSON.parse(raw)
    } catch {
      return null
    }
  })

  const signedIn = computed(() => !!user.value)

  function close() {
    emit('update:visible', false)
  }

  function formatRating(value: number | undefined | null) {
    if (value == null || Number.isNaN(Number(value))) return '0.0'
    return Number(value).toFixed(1)
  }

  function seedDefaults() {
    categories.value.forEach(cat => {
      if (ratingInputs.value[cat.category_id] == null) ratingInputs.value[cat.category_id] = 3
      if (commentInputs.value[cat.category_id] == null) commentInputs.value[cat.category_id] = ''
    })
  }

  async function loadCategories() {
    isLoading.value = true
    error.value = ''
    try {
      const data = await apiGet('/ratings/categories')
      categories.value = Array.isArray(data) ? data : []
      seedDefaults()
    } catch (err) {
      console.error('Failed to load rating categories:', err)
      error.value = 'Unable to load rating categories.'
      categories.value = []
    } finally {
      isLoading.value = false
    }
  }

  async function loadSpotRatings() {
    if (!props.spot) {
      categoryStats.value = {}
      return
    }
    try {
      const data = await apiGet(`/ratings/spot/${props.spot.id}`)
      const map: Record<number, { avg_rating: number; vote_count: number }> = {}
      if (Array.isArray(data)) {
        data.forEach((entry: any) => {
          map[Number(entry.category_id)] = {
            avg_rating: Number(entry.avg_rating ?? 0),
            vote_count: Number(entry.vote_count ?? 0)
          }
        })
      }
      categoryStats.value = map
    } catch (err) {
      console.error('Failed to load spot ratings:', err)
    }
  }

  async function loadUserVotesForSpot() {
    if (!user.value || !props.spot) {
      userVotes.value = {}
      return
    }

    try {
      const data = await apiGet(`/ratings/user/${user.value.student_id}`)
      userVotes.value = {}
      if (Array.isArray(data)) {
        data.forEach((vote: any) => {
          if (vote.spot_id === props.spot?.id) {
            userVotes.value[vote.category_id] = vote
            // Pre-fill the form with user's existing vote if it exists
            ratingInputs.value[vote.category_id] = vote.rating
          }
        })
      }
    } catch (err) {
      console.error('Failed to load user votes:', err)
    }
  }

  async function refreshData() {
    await loadCategories()
    await loadSpotRatings()
    await loadUserVotesForSpot()
  }

  async function submitRating(categoryId: number) {
    error.value = ''
    success.value = ''

    if (!signedIn.value) {
      emit('require-auth')
      return
    }
    if (!props.spot) {
      error.value = 'No study spot selected.'
      return
    }

    const rating = ratingInputs.value[categoryId] ?? 3
    const categorySlug = categories.value.find(c => c.category_id === categoryId)?.slug

    if (!categorySlug) {
      error.value = 'Category not found.'
      return
    }

    isSubmitting.value = true
    try {
      // Submit to backend with new API (converts 1-5 rating to direction)
      const direction = rating >= 4 ? 1 : -1
      await submitVoteToBackend(user.value.student_id, props.spot.id, categorySlug, direction)
      
      success.value = 'Rating saved.'
      await loadSpotRatings()
      await loadUserVotesForSpot()
      window.dispatchEvent(new CustomEvent('ratings-updated', { detail: { spotId: props.spot.id } }))
      window.dispatchEvent(new CustomEvent('votes-changed', { detail: { spotId: props.spot.id, category: categorySlug } }))
    } catch (err) {
      console.error('Failed to submit rating:', err)
      error.value = 'Unable to submit rating. Please try again.'
    } finally {
      isSubmitting.value = false
    }
  }

  watch(() => props.visible, (v) => {
    if (v) {
      success.value = ''
      error.value = ''
      refreshData()
    }
  })

  watch(() => props.spot?.id, () => {
    if (props.visible) refreshData()
  })
</script>
