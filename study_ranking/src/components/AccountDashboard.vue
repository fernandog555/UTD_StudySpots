<script setup lang="ts">
  import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
  import { useRouter } from 'vue-router'
  import AccountSettings from './AccountSettings.vue'

  const props = defineProps<{
    username: string | null
  }>()

  const emit = defineEmits<{
    (e: 'close'): void
  }>()

  const router = useRouter()

  // UI state
  const showSettings = ref(false)

  function openSavedView() {
    router.push({ name: 'bookmarks' })
    emit('close')
  }

  function openSettings() {
    showSettings.value = true
  }

  function openMyReviews() {
    router.push({ name: 'my-reviews' })
    emit('close')
  }

  function openContributions() {
    router.push({ name: 'contributions' })
    emit('close')
  }

  function close() {
    emit('close')
  }

  function signOut() {
    localStorage.removeItem('username')
    localStorage.removeItem('user')
    localStorage.removeItem('bookmarks')
    window.dispatchEvent(new CustomEvent('bookmarks-changed', { detail: { id: null, bookmarked: false } }))
    window.dispatchEvent(new CustomEvent('account-changed', { detail: null }))
    emit('close')
  }

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Escape') {
      close()
    }
  }

  onMounted(() => {
    window.addEventListener('keydown', handleKeyDown)
  })

  onBeforeUnmount(() => {
    window.removeEventListener('keydown', handleKeyDown)
  })

  watch(() => props.username, (nv) => {
    if (!nv) emit('close')
  })
</script>

<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center">
    <div class="absolute inset-0 bg-black/50 backdrop-blur-custom" @click="close"></div>

    <div class="relative bg-[var(--bg)] rounded-xl shadow-xl w-full max-w-3xl p-6 z-10">
      <button class="absolute top-4 right-4 text-xl font-bold cursor-pointer hover:text-red-500" @click="close">
        ✕
      </button>

      <h2 class="text-2xl font-semibold mb-4">Welcome {{ props.username }}</h2>

      <p class="mb-4 text-[var(--dark5)]">Manage Your Account</p>

      <!-- Account dashboard -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="p-4 border rounded bg-[var(--bg_highlight)] opacity-90 hover:cursor-pointer"
             @click="openSavedView">
          <h3 class="font-semibold mb-2">Saved Spots</h3>
          <p class="text-sm text-[var(--dark5)]">Bookmark study spots for quick access.</p>
        </div>

        <div class="p-4 border rounded bg-[var(--bg_highlight)] opacity-90 hover:cursor-pointer"
             @click="openMyReviews">
          <h3 class="font-semibold mb-2">My Reviews</h3>
          <p class="text-sm text-[var(--dark5)]">View and manage your spot reviews.</p>
        </div>

        <div class="p-4 border rounded bg-[var(--bg_highlight)] opacity-90 hover:cursor-pointer"
             @click="openContributions">
          <h3 class="font-semibold mb-2">Contributions</h3>
          <p class="text-sm text-[var(--dark5)]">Submit new study spots, edit existing ones and view your votes.</p>
        </div>

        <div class="p-4 border rounded bg-[var(--bg_highlight)] opacity-90 hover:cursor-pointer"
             @click="openSettings">
          <h3 class="font-semibold mb-2">Account Settings</h3>
          <p class="text-sm text-[var(--dark5)]">Manage account settings.</p>
        </div>
      </div>

      <div class="mt-6 flex gap-3 justify-end">
        <button class="px-4 py-2 border rounded hover:bg-[var(--bg_highlight)]" @click="close">Close</button>
        <button class="px-6 py-2 rounded-md text-base text-center hover:cursor-pointer hover:bg-(--red1)/10 border text-(--red1) border-(--red1)" @click="signOut">Sign Out</button>
      </div>
    </div>

    <!-- Account settings overlay -->
    <AccountSettings v-if="showSettings"
                     :username="props.username"
                     @close="showSettings = false" />
  </div>
</template>
