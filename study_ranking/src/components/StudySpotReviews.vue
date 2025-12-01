<template>
  <div ref="root" :class="containerClass" :style="rootStyle" @click.stop>
    <!-- Fixed header -->
    <div ref="headerRef" class="flex-none bg-(--bg) z-10 pb-2 border-b border-(--dark3) px-4 sm:px-6 pt-2">
      <button class="absolute top-2 sm:top-4 right-2 sm:right-4 text-lg sm:text-xl font-bold cursor-pointer hover:text-red-500 z-20" @click="$emit('close')">
        ✕
      </button>

      <h3 class="text-xl sm:text-2xl md:text-3xl mb-3 sm:mb-4 pr-16 break-words">Reviews for {{ spot?.name }}</h3>
    </div>

    <!-- Scrollable content area -->
    <div class="flex-1 overflow-y-auto px-4 sm:px-6 py-4" :style="scrollAreaStyle">
      <div v-if="isLoading" class="text-(--dark5)">
        <p>Loading reviews…</p>
      </div>

      <div v-else-if="loadError" class="text-red-500 text-sm" role="alert">{{ loadError }}</div>

      <div v-else-if="reviews.length === 0" class="text-(--dark5)">
        <p>No reviews available.</p>
      </div>

      <ul v-else class="space-y-4">
        <li v-for="(r, idx) in reviews" :key="idx" class="p-4 border rounded bg-(--bg_highlight)">
          <div class="flex justify-between items-start">
            <div class="flex-1 min-w-0">
              <p class="font-semibold break-words">{{ r.author }}</p>
              <p class="text-sm text-(--dark5)">{{ r.date }}</p>
            </div>
            <div class="text-yellow-500 font-bold whitespace-nowrap ml-2 flex-none">{{ formatRating(r.rating) }} / 5</div>
          </div>
          <p class="mt-2 text-(--dark5) break-words whitespace-pre-wrap">{{ r.text }}</p>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
  import StudySpot from '../classes/spot.ts'
  import { computed, ref, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
  import { getReviewsForSpot, fetchReviewsForSpot } from '../data/reviewsMap'
  import { useSyncedHeaderHeight } from '../composables/useSyncedHeaderHeight'

  const props = defineProps<{
    spot: StudySpot | null
    variant?: 'modal' | 'panel'
  }>()

  const emit = defineEmits<{
    (e: 'close'): void
  }>()

  const reviews = computed(() => {
    if (!props.spot) return []
    return getReviewsForSpot(props.spot.id)
  })

  const isLoading = ref(false)
  const loadError = ref('')

  const root = ref<HTMLElement | null>(null)

  // Use synced header height composable
  const { headerRef } = useSyncedHeaderHeight()

  const containerClass = computed(() => {
    if (props.variant === 'panel') {
      return 'relative bg-(--bg) rounded-lg shadow-xl flex flex-col overflow-hidden'
    }
    return 'relative bg-(--bg) rounded-xl shadow-xl w-full max-w-2xl flex flex-col overflow-hidden'
  })

  const rootStyle = computed(() => {
    if (props.variant === 'panel') {
      // Match StudySpotDetails - allow scaling to minimum
      return {
        width: 'min(600px, 100vw - 1rem)',
        minWidth: '360px',
        maxWidth: '600px',
        height: 'min(700px, 100vh - 1rem)',
        minHeight: '420px',
        maxHeight: '700px',
        boxSizing: 'border-box',
        padding: '0',
        flex: '0 0 auto',
        display: 'flex',
        flexDirection: 'column'
      }
    }
    return {
      height: '700px',
      minHeight: '700px',
      maxHeight: '700px',
      display: 'flex',
      flexDirection: 'column'
    }
  })

  const scrollAreaStyle = computed(() => {
    // Let flexbox handle the height with flex-1
    return {
      minHeight: '0' // Critical for flexbox scroll containers
    }
  })

  function formatRating(value: number | null | undefined) {
    if (value == null || Number.isNaN(Number(value))) return '0.0'
    return Number(value).toFixed(1)
  }

  async function loadReviews() {
    if (!props.spot?.id) return
    isLoading.value = true
    loadError.value = ''
    try {
      await fetchReviewsForSpot(props.spot.id)
    } catch (err) {
      console.error('Failed to load reviews:', err)
      loadError.value = 'Unable to load reviews right now.'
    } finally {
      isLoading.value = false
    }
  }

  let resizeObserver: ResizeObserver | null = null

  onMounted(async () => {
    await nextTick()

    loadReviews()

    // Listen for resize events from the details component
    const handleResize = () => {
      // Force re-render if needed
      if (root.value && props.variant === 'panel') {
        // Let CSS handle the sizing with clamp
        root.value.style.width = getComputedStyle(root.value).width
        root.value.style.height = getComputedStyle(root.value).height
      }
    }
    window.addEventListener('resize', handleResize)

    // Initial sizing
    handleResize()
    window.addEventListener('reviews-changed', onReviewsChanged)
  })

  onBeforeUnmount(() => {
    if (resizeObserver) {
      resizeObserver.disconnect()
      resizeObserver = null
    }
    window.removeEventListener('reviews-changed', onReviewsChanged)
  })

  watch(() => props.variant, () => {
    nextTick()
  })

  watch(() => reviews.value, () => {
    // Re-render when reviews change
    nextTick()
  })

  watch(() => props.spot?.id, () => {
    loadReviews()
  })

  function onReviewsChanged(e: Event) {
    const detail = (e as CustomEvent).detail
    if (props.spot && detail?.spotId === props.spot.id) {
      loadReviews()
    }
  }
</script>
