<script setup lang="ts">
  import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
  import router from '../router'
  import AccountDashboard from './AccountDashboard.vue'
  import Account from './Account.vue'

  const query = ref('')

  function getStoredUsername() {
    const userRaw = localStorage.getItem('user')
    if (userRaw) {
      try {
        const parsed = JSON.parse(userRaw)
        if (parsed?.netid) return parsed.netid as string
      } catch {
        // fall through
      }
    }
    return localStorage.getItem('username')
  }

  const username = ref<string | null>(getStoredUsername());

  // local UI state to show account dashboard component
  const showAccount = ref(false)

  // modal state for sign in / sign up
  const showAccountModal = ref(false)

  function search() {
    const q = query.value.trim()
    if (q) {
      router.push({ name: 'search', params: { query: q } })
    } else {
      router.push({ name: 'search' })
    }
  }

  function navigate(location: string) {
    query.value = ''
    router.push(location)
  }

  function openAccount() {
    if (username.value) {
      showAccount.value = true
    } else {
      showAccountModal.value = true
    }
  }

  // listen for account-changed events
  function normalizeUser(detail: any): string | null {
    if (!detail) return null
    if (typeof detail === 'string') return detail
    if (typeof detail === 'object') {
      if (detail.netid) return String(detail.netid)
      if (detail.username) return String(detail.username)
    }
    return null
  }

  function onAccountChanged(e: Event) {
    const detail = (e as CustomEvent).detail
    username.value = normalizeUser(detail)
    if (!username.value) {
      // close dashboard if user signs out elsewhere
      showAccount.value = false
    }
  }

  onMounted(() => {
    window.addEventListener('account-changed', onAccountChanged as EventListener)
  })

  onBeforeUnmount(() => {
    window.removeEventListener('account-changed', onAccountChanged as EventListener)
  })
</script>

<template>
  <div class="text-2xl px-8 py-4 w-full h-24 bg-(--terminal_black) flex items-center gap-6">
    <!-- Home Button -->
    <button @click="navigate('/')"
            class="border-2 rounded-md px-4 py-2 hover:bg-(--bg_highlight) hover:cursor-pointer">
      Home
    </button>

    <!-- Search Input -->
    <div class="flex-grow">
      <input @keypress.enter="search"
             class="border-2 rounded-md w-full px-4 py-2"
             placeholder="Search Study Spots. (Submit on Empty to View All Spots)"
             v-model="query" />
    </div>

    <!-- Account Button -->
    <button @click="openAccount"
            class="border-2 rounded-md px-4 py-2 hover:bg-(--bg_highlight) hover:cursor-pointer">
      <span v-if="username">{{ username }}</span>
      <span v-else>Sign Up / Sign In</span>
    </button>
  </div>

  <!-- account dashboard modal -->
  <AccountDashboard v-if="showAccount"
                    :username="username"
                    @close="showAccount = false; username = getStoredUsername()" />

  <!-- account modal -->
  <Account v-if="showAccountModal"
                initialMode="login"
                @close="showAccountModal = false; username = getStoredUsername()" />
</template>
