import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'

const sharedHeaderHeight = ref<number>(0)
const headerRefs = new Set<HTMLElement>()

export function useSyncedHeaderHeight() {
  const headerRef = ref<HTMLElement | null>(null)
  const currentHeight = ref<number>(0)
  let resizeObserver: ResizeObserver | null = null

  const updateHeight = () => {
    if (headerRef.value) {
      const height = headerRef.value.offsetHeight
      currentHeight.value = height

      // Update shared max height if this header is taller
      if (height > sharedHeaderHeight.value) {
        sharedHeaderHeight.value = height
      } else {
        // Recalculate max height from all registered headers
        let maxHeight = 0
        headerRefs.forEach(ref => {
          maxHeight = Math.max(maxHeight, ref.offsetHeight)
        })
        sharedHeaderHeight.value = maxHeight
      }
    }
  }

  onMounted(async () => {
    await nextTick()

    if (headerRef.value) {
      headerRefs.add(headerRef.value)

      // Create ResizeObserver to watch for size changes
      resizeObserver = new ResizeObserver(() => {
        updateHeight()
      })

      resizeObserver.observe(headerRef.value)
      updateHeight()
    }
  })

  onBeforeUnmount(() => {
    if (resizeObserver) {
      resizeObserver.disconnect()
      resizeObserver = null
    }

    if (headerRef.value) {
      headerRefs.delete(headerRef.value)

      // Recalculate max height after removing this header
      let maxHeight = 0
      headerRefs.forEach(ref => {
        maxHeight = Math.max(maxHeight, ref.offsetHeight)
      })
      sharedHeaderHeight.value = maxHeight
    }
  })

  // Watch for changes in shared height
  watch(sharedHeaderHeight, (newHeight) => {
    if (headerRef.value && newHeight > currentHeight.value) {
      headerRef.value.style.minHeight = `${newHeight}px`
    }
  })

  return {
    headerRef,
    sharedHeaderHeight
  }
}
