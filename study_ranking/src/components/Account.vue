<template>
  <div class="w-full h-full bg-black/50 backdrop-blur-custom z-50 inset-0 fixed flex justify-center items-center p-2 sm:p-4"
       @click.self="close">
    <div class="relative w-full max-w-3xl">
      <div class="mx-auto w-full bg-[var(--bg)] text-[var(--blue)]
               flex flex-col items-center justify-start gap-4 sm:gap-6 p-4 sm:p-6 md:p-8 lg:p-10 rounded-xl shadow-xl relative
               max-h-[90vh] overflow-y-auto"
           @click.stop>
        <button class="absolute top-3 sm:top-5 right-3 sm:right-5 text-xl sm:text-2xl font-bold cursor-pointer hover:text-red-500 z-10"
                @click="close">
          ✕
        </button>

        <!-- Mode toggle -->
        <div class="flex items-center gap-2 sm:gap-4 w-full sm:w-auto">
          <button @click="switchMode('login')"
                  :class="['px-3 sm:px-5 py-2 sm:py-3 rounded-md text-base sm:text-lg w-32 sm:w-40 text-center hover:cursor-pointer', mode === 'login' ? 'bg-(--fg_gutter) border border-(--magenta) text-(--magenta)' : 'border']">
            Sign In
          </button>

          <button @click="switchMode('create')"
                  :class="['px-3 sm:px-5 py-2 sm:py-3 rounded-md text-base sm:text-lg w-32 sm:w-40 text-center hover:cursor-pointer', mode === 'create' ? 'bg-(--fg_gutter) border border-(--magenta) text-(--magenta)' : 'border']">
            Sign Up
          </button>
        </div>

        <h2 class="text-2xl sm:text-3xl font-semibold text-center">
          {{ mode === 'login' ? 'Welcome Back' : 'Create User Account' }}
        </h2>

        <div class="w-full max-w-md flex flex-col items-center gap-3 sm:gap-4">
          <div class="w-full">
            <label class="block text-sm mb-2">NetID</label>
            <input class="w-full text-base sm:text-lg py-2 sm:py-3 px-3 sm:px-4 border-b-2 mb-2"
                   placeholder="Enter NetID" v-model="username" />
          </div>

          <div class="w-full">
            <label class="block text-sm mb-2">Password</label>
            <div class="relative">
              <input :type="showPassword ? 'text' : 'password'"
                     class="w-full text-base sm:text-lg py-2 sm:py-3 px-3 sm:px-4 border-b-2 mb-2"
                     placeholder="Enter Password" v-model="password" />
              <button type="button"
                      class="absolute right-2 sm:right-3 top-1/2 -translate-y-1/2 text-xs sm:text-sm text-[var(--fg_dark)] hover:cursor-pointer"
                      @click="showPassword = !showPassword">
                {{ showPassword ? 'Hide' : 'Show' }}
              </button>
            </div>
          </div>

          <div v-if="errorMessage" class="text-red-500 text-center w-full text-sm sm:text-base">
            {{ errorMessage }}
          </div>

          <div class="w-full flex justify-center">
            <button @click="validateAndSubmit(mode)"
                    class="border px-6 sm:px-10 py-2 sm:py-3 bg-(--bg_highlight) text-(--blue) rounded-md hover:bg-(--bg_dark1) text-base sm:text-lg w-full sm:w-auto hover:cursor-pointer">
              {{ mode === 'login' ? 'Login' : 'Create Account' }}
            </button>
          </div>
        </div>

        <!-- Centered info box -->
        <div class="w-full max-w-md min-h-[140px] sm:min-h-[160px]">
          <div v-if="mode === 'create'" class="bg-[var(--bg_highlight)] p-4 sm:p-6 rounded-md border text-center h-full">
            <h3 class="text-xl sm:text-2xl font-semibold mb-2 sm:mb-3">Account requirements</h3>
            <ul class="list-disc pl-4 sm:pl-5 text-left leading-relaxed mx-auto max-w-sm text-sm sm:text-base">
              <li><strong>NetID:</strong> at least 3 characters</li>
              <li><strong>Password:</strong> at least 6 characters</li>
              <li>Use the same credentials to log in and submit ratings or new spots.</li>
            </ul>
          </div>

          <div v-else class="bg-[var(--bg_highlight)] p-4 sm:p-6 rounded-md border text-center h-full flex items-center justify-center">
            <div>
              <h3 class="text-xl sm:text-2xl font-semibold mb-2 sm:mb-3">Welcome back</h3>
              <p class="leading-relaxed text-sm sm:text-base">
                Great to see you again — sign in and continue discovering study spots, saving favorites, and contributing reviews.
              </p>
            </div>
          </div>
        </div>

        <!-- SQL injection vs prepared statement demo for login -->
        <div v-if="mode === 'login'" class="w-full max-w-3xl flex flex-col gap-3 sm:gap-4">
          <div>
            <h3 class="text-xl sm:text-2xl font-semibold mb-1">SQL Injection Demo (Login)</h3>
            <p class="text-sm sm:text-base text-(--fg_dark)">
              The raw string-concatenated query is vulnerable. Try a password like <code>' OR '1'='1' --</code> to see how it would change the unsafe query.
              The prepared statement keeps the inputs as bound parameters.
            </p>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-3 sm:gap-4">
            <div class="border rounded-md p-3 sm:p-4 bg-(--bg_dark1)">
              <div class="text-xs uppercase tracking-wide text-(--magenta) mb-2">Vulnerable (string concat)</div>
              <pre class="text-xs sm:text-sm whitespace-pre-wrap leading-snug bg-(--bg) p-3 rounded-md border overflow-auto">{{ unsafeQuery }}</pre>
            </div>

            <div class="border rounded-md p-3 sm:p-4 bg-(--bg_dark1)">
              <div class="text-xs uppercase tracking-wide text-green-400 mb-2">Safe (prepared statement)</div>
              <pre class="text-xs sm:text-sm whitespace-pre-wrap leading-snug bg-(--bg) p-3 rounded-md border overflow-auto">{{ preparedQuery }}</pre>
              <div class="text-xs sm:text-sm mt-2 text-(--fg_dark)">
                Parameters: [{{ preparedParams[0] }}, {{ preparedParams[1] }}]
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ref, onMounted, onBeforeUnmount, watch, computed } from 'vue'
  import { useRouter } from 'vue-router'
  import { apiPost } from '../api'

  const props = defineProps<{
    initialMode?: 'login' | 'create'
  }>()

  const emit = defineEmits<{
    (e: 'close'): void
  }>()

  const router = useRouter()

  const username = ref('')
  const password = ref('')
  const errorMessage = ref('')
  const mode = ref<'login' | 'create'>(props.initialMode ?? 'login')

  // show/hide password toggle
  const showPassword = ref(false)

  // SQL strings for the assignment demo (login only)
  const unsafeQuery = computed(() => {
    const u = username.value || '...'
    const p = password.value || '...'
    return `SELECT student_id, netid
FROM students
WHERE netid = '${u}' AND hashed_password = '${p}';`
  })

  const preparedQuery = computed(() => {
    return `SELECT student_id, netid
FROM students
WHERE netid = $1 AND hashed_password = $2;`
  })

  const preparedParams = computed(() => [username.value || '...', password.value || '...'])

  function isValidUsername(name: string): boolean {
    return name.trim().length >= 3
  }

  function isValidPassword(pass: string): boolean {
    return pass.trim().length >= 6
  }

  async function validateAndSubmit(action: 'login' | 'create') {
    errorMessage.value = ''

    if (!isValidUsername(username.value)) {
      errorMessage.value = 'NetID must be at least 3 characters.'
      return
    }

    if (!isValidPassword(password.value)) {
      errorMessage.value = 'Password must be at least 6 characters.'
      return
    }

    try {
      const endpoint = action === 'login' ? '/auth/login' : '/auth/register'
      const user = await apiPost(endpoint, {
        netid: username.value.trim(),
        password: password.value
      })

      localStorage.setItem('user', JSON.stringify(user))
      localStorage.setItem('username', user.netid || username.value.trim())
      window.dispatchEvent(new CustomEvent('account-changed', { detail: user }))

      emit('close')
      router.push('/')
    } catch (err: any) {
      console.error(err)
      errorMessage.value = err?.message || 'Authentication failed. Please try again.'
    }
  }

  function switchMode(m: 'login' | 'create') {
    mode.value = m
  }

  function close() {
    emit('close')
  }

  const handleKeys = (e: KeyboardEvent) => {
    if (e.key === 'Escape') {
      close()
    }
  }

  onMounted(() => {
    window.addEventListener('keydown', handleKeys)
  })

  onBeforeUnmount(() => {
    window.removeEventListener('keydown', handleKeys)
  })

  watch(() => props.initialMode, (newMode) => {
    if (newMode) mode.value = newMode
  })
</script>
