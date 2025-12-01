<template>
  <div class="fixed inset-0 z-60 flex items-center justify-center">
    <div class="absolute inset-0 backdrop-blur-custom" @click="close"></div>

    <div class="relative bg-[var(--bg)] rounded-xl shadow-xl w-full max-w-md p-6 z-10">
      <button class="absolute top-4 right-4 text-xl font-bold cursor-pointer hover:text-red-500" @click="close">
        ✕
      </button>

      <h2 class="text-2xl font-semibold mb-4">Account Settings</h2>

      <p class="mb-4 text-[var(--dark5)]">Change your username or password.</p>

      <div class="flex gap-2 mb-4 items-center justify-center">
        <button :class="['text-sm px-3 sm:px-2 py-1 sm:py-2 rounded-md text-base w-32 sm:w-40 text-center hover:cursor-pointer', tab === 'username' ? 'bg-(--fg_gutter) border border-(--magenta) text-(--magenta)' : 'border']"
                @click="tab = 'username'">
          Change Username
        </button>
        <button :class="['text-sm px-3 sm:px-2 py-1 sm:py-2 rounded-md text-base w-32 sm:w-40 text-center hover:cursor-pointer', tab === 'password' ? 'bg-(--fg_gutter) border border-(--magenta) text-(--magenta)' : 'border']"
                @click="tab = 'password'">
          Change Password
        </button>
      </div>

      <div v-if="tab === 'username'" class="space-y-4">
        <div>
          <label class="block text-sm mb-1">Current Username</label>
          <input v-model="oldUsername"
                 class="w-full text-lg py-2 px-3 border-b-2"
                 autocomplete="username" />
        </div>

        <div>
          <label class="block text-sm mb-1">New Username</label>
          <input v-model="newUsername"
                 class="w-full text-lg py-2 px-3 border-b-2"
                 placeholder="Enter new username" />
        </div>

        <div v-if="errorMessage" class="text-red-500 text-sm">
          {{ errorMessage }}
        </div>

        <div class="flex justify-end gap-3 mt-2">
          <button class="px-4 py-2 border rounded hover:bg-[var(--bg_highlight)]" @click="close">Cancel</button>
          <button class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700" @click="onSaveClick('username')">Save</button>
        </div>
      </div>

      <div v-else class="space-y-4">
        <div>
          <label class="block text-sm mb-1">Current Password</label>
          <div class="relative">
            <input :type="showOldPassword ? 'text' : 'password'"
                   v-model="oldPassword"
                   class="w-full text-lg py-2 px-3 border-b-2"
                   placeholder="Enter current password" />
            <button type="button"
                    class="hover:cursor-pointer absolute right-3 top-1/2 -translate-y-1/2 text-sm text-[var(--fg_dark)]"
                    @click="showOldPassword = !showOldPassword">
              {{ showOldPassword ? 'Hide' : 'Show' }}
            </button>
          </div>
        </div>

        <div>
          <label class="block text-sm mb-1">New Password</label>
          <div class="relative">
            <input :type="showNewPassword ? 'text' : 'password'"
                   v-model="newPassword"
                   class="w-full text-lg py-2 px-3 border-b-2"
                   placeholder="Enter new password" />
            <button type="button"
                    class="hover:cursor-pointer absolute right-3 top-1/2 -translate-y-1/2 text-sm text-[var(--fg_dark)]"
                    @click="showNewPassword = !showNewPassword">
              {{ showNewPassword ? 'Hide' : 'Show' }}
            </button>
          </div>
        </div>

        <div>
          <label class="block text-sm mb-1">Confirm New Password</label>
          <div class="relative">
            <input :type="showConfirmPassword ? 'text' : 'password'"
                   v-model="confirmNewPassword"
                   class="w-full text-lg py-2 px-3 border-b-2"
                   placeholder="Confirm new password" />
            <button type="button"
                    class="hover:cursor-pointer absolute right-3 top-1/2 -translate-y-1/2 text-sm text-[var(--fg_dark)]"
                    @click="showConfirmPassword = !showConfirmPassword">
              {{ showConfirmPassword ? 'Hide' : 'Show' }}
            </button>
          </div>
        </div>

        <div v-if="errorMessage" class="text-red-500 text-sm">
          {{ errorMessage }}
        </div>

        <div class="flex justify-end gap-3 mt-2">
          <button class="px-4 py-2 border rounded hover:bg-[var(--bg_highlight)]" @click="close">Cancel</button>
          <button class="border px-6 sm:px-10 py-2 sm:py-3 bg-(--bg_highlight) text-(--blue) rounded-md hover:bg-(--bg_dark1) text-base sm:text-lg w-full sm:w-auto hover:cursor-pointer" @click="onSaveClick('password')">Save</button>
        </div>
      </div>
    </div>

    <!-- Confirmation popup -->
    <div v-if="showConfirm" class="fixed inset-0 z-70 flex items-center justify-center">
      <div class="absolute inset-0 backdrop-blur-custom" @click="cancelConfirm"></div>
      <div class="relative bg-[var(--bg)] rounded-lg shadow-xl w-[90%] max-w-sm p-5 z-80">
        <h3 class="text-lg font-semibold mb-3">Confirm change</h3>
        <p class="mb-4">{{ confirmMessage }}</p>
        <div class="flex justify-end gap-3">
          <button class="px-3 py-1 border rounded" @click="cancelConfirm">Cancel</button>
          <button class="px-3 py-1 bg-blue-600 text-white rounded" @click="confirmSave">Confirm</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
  import { updateUserProfile } from '@/api'

  const props = defineProps<{
    username: string | null
  }>()

  const emit = defineEmits<{
    (e: 'close'): void
  }>()

  const tab = ref<'username' | 'password'>('username')

  const currentUsername = ref<string>('')
  const studentId = ref<number | null>(null)

  const oldUsername = ref('')
  const newUsername = ref('')

  const oldPassword = ref('')
  const newPassword = ref('')

  const confirmNewPassword = ref('')
  const showOldPassword = ref(false)
  const showNewPassword = ref(false)
  const showConfirmPassword = ref(false)

  const errorMessage = ref('')

  // confirmation dialog state
  const showConfirm = ref(false)
  const confirmType = ref<'username' | 'password' | null>(null)
  const confirmMessage = ref('')

  function isValidUsername(name: string): boolean {
    return name.length >= 8
  }

  function isValidPassword(pass: string): boolean {
    const regex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]).{8,}$/
    return regex.test(pass)
  }

  // validation functions return true if valid and set errorMessage on failure
  function validateUsernameChange(): boolean {
    errorMessage.value = ''
    if (!studentId.value) {
      errorMessage.value = 'You must be signed in to update your username.'
      return false
    }
    if (!oldUsername.value) {
      errorMessage.value = 'Please enter your current username.'
      return false
    }
    if (!isValidUsername(newUsername.value)) {
      errorMessage.value = 'New username must be at least 8 characters.'
      return false
    }
    return true
  }

  function validatePasswordChange(): boolean {
    errorMessage.value = ''
    if (!studentId.value) {
      errorMessage.value = 'You must be signed in to update your password.'
      return false
    }
    if (!oldPassword.value) {
      errorMessage.value = 'Please enter your current password.'
      return false
    }
    if (!newPassword.value || !confirmNewPassword.value) {
      errorMessage.value = 'Enter and confirm your new password.'
      return false
    }
    if (newPassword.value !== confirmNewPassword.value) {
      errorMessage.value = 'New passwords do not match.'
      return false
    }
    if (!isValidPassword(newPassword.value)) {
      errorMessage.value = 'Password must be at least 8 chars and include uppercase, lowercase, number, and special character.'
      return false
    }
    return true
  }

  // prepareSave validates then opens confirmation dialog
  function onSaveClick(type: 'username' | 'password') {
    if (type === 'username') {
      if (!validateUsernameChange()) return
      confirmType.value = 'username'
      confirmMessage.value = 'Are you sure you want to change your username?'
    } else {
      if (!validatePasswordChange()) return
      confirmType.value = 'password'
      confirmMessage.value = 'Are you sure you want to change your password?'
    }
    showConfirm.value = true
  }

  function cancelConfirm() {
    showConfirm.value = false
    confirmType.value = null
    // leave form values intact so user can edit
  }

  async function commitUsername() {
    if (!studentId.value) return
    try {
      const updated = await updateUserProfile({ student_id: studentId.value, netid: newUsername.value })
      localStorage.setItem('user', JSON.stringify(updated))
      localStorage.setItem('username', updated.netid)
      window.dispatchEvent(new CustomEvent('account-changed', { detail: updated }))
      emit('close')
    } catch (error: any) {
      errorMessage.value = error?.message || 'Failed to update username.'
    }
  }

  async function commitPassword() {
    if (!studentId.value) return
    try {
      await updateUserProfile({
        student_id: studentId.value,
        password: newPassword.value,
        current_password: oldPassword.value
      })
      emit('close')
    } catch (error: any) {
      errorMessage.value = error?.message || 'Failed to update password.'
    }
  }

  async function confirmSave() {
    if (confirmType.value === 'username') {
      await commitUsername()
    } else if (confirmType.value === 'password') {
      await commitPassword()
    }
    showConfirm.value = false
    confirmType.value = null
  }

  function close() {
    emit('close')
  }

  const handleKey = (e: KeyboardEvent) => {
    if (showConfirm.value) {
      if (e.key === 'Escape') cancelConfirm()
      if (e.key === 'Enter') confirmSave()
      return
    }
    if (e.key === 'Escape') close()
    if (e.key === 'Enter') {
      if (tab.value === 'username') onSaveClick('username')
      else onSaveClick('password')
    }
  }

  onMounted(() => {
    // prefill from stored user
    try {
      const raw = localStorage.getItem('user')
      if (raw) {
        const parsed = JSON.parse(raw)
        studentId.value = parsed?.student_id ?? null
        currentUsername.value = parsed?.netid ?? ''
      }
    } catch {
      studentId.value = null
      currentUsername.value = ''
    }
    if (!currentUsername.value) currentUsername.value = props.username ?? (localStorage.getItem('username') ?? '')
    oldUsername.value = currentUsername.value
    window.addEventListener('keydown', handleKey)
  })

  onBeforeUnmount(() => {
    window.removeEventListener('keydown', handleKey)
  })

  watch(() => props.username, (v) => {
    currentUsername.value = v ?? (localStorage.getItem('username') ?? '')
    oldUsername.value = currentUsername.value
  })
</script>
