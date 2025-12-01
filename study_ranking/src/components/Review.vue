<template>
  <div class="fixed inset-0 z-60 flex items-center justify-center bg-black/40 p-4" @click.self="$emit('close')">
    <div class="bg-(--bg) rounded-lg shadow-xl w-full max-w-xl p-6 px-10 relative">
      <button class="absolute top-4 right-4 text-xl font-bold cursor-pointer hover:text-red-500" @click="$emit('close')">✕</button>
      <h3 class="text-3xl font-semibold mb-4 pr-12 break-words">Write a review for {{ spot?.name }}</h3>

      <!-- submission-level error -->
      <p v-if="submitError" class="text-sm text-red-400 mb-2" role="alert" aria-live="assertive">
        {{ submitError }}
      </p>

      <form @submit.prevent="submit" class="space-y-4" novalidate>
        <div>
          <label class="block text-sm font-medium mb-1" for="author">Your name</label>
          <input id="author"
                 v-model="author"
                 type="text"
                 :aria-invalid="touchedAuthor && !authorValid ? 'true' : 'false'"
                 class="w-full p-2 border rounded"
                 @blur="touchedAuthor = true" />
          <p v-if="touchedAuthor && !authorValid" class="text-sm text-red-400 mt-1" role="alert" aria-live="polite">
            <span v-if="usernamePresent">Name must match your username.</span>
            <span v-else>Please enter your name.</span>
          </p>
        </div>

        <div>
          <label class="block text-sm font-medium mb-1">Rating</label>
          <div class="flex items-center gap-2" role="radiogroup" :aria-label="`Rating for ${spot?.name || 'spot'}`">
            <button v-for="n in 5"
                    :key="n"
                    type="button"
                    class="w-8 h-8 flex items-center justify-center rounded hover:bg-black/10 transition"
                    :aria-pressed="rating === n"
                    :title="`${n} star${n > 1 ? 's' : ''}`"
                    @click="setRating(n)"
                    @keydown.enter.prevent="setRating(n)">
              <svg v-if="rating >= n" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="w-5 h-5 text-yellow-400 fill-current" aria-hidden="true">
                <path d="M12 .587l3.668 7.431L23.5 9.75l-5.75 5.6L19.336 24 12 20.013 4.664 24l1.586-8.65L.5 9.75l7.832-1.732L12 .587z" />
              </svg>

              <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="w-5 h-5 text-(--dark5)" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 .587l3.668 7.431L23.5 9.75l-5.75 5.6L19.336 24 12 20.013 4.664 24l1.586-8.65L.5 9.75l7.832-1.732L12 .587z" />
              </svg>
            </button>
            <div class="text-sm text-(--dark5) ml-2">{{ rating }} / 5</div>
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium mb-1" for="date">Date</label>
          <input id="date" v-model="date" type="date" class="p-2 border rounded" />
        </div>

        <div class="relative">
          <label class="block text-sm font-medium mb-1" for="text">Review</label>
          <textarea id="text"
                    v-model="text"
                    rows="5"
                    class="w-full p-2 border rounded resize-y"
                    @input="onTextInput"
                    @blur="touchedText = true"
                    :aria-invalid="touchedText && !validCharCount ? 'true' : 'false'"></textarea>

          <!-- character count in bottom-right corner -->
          <div class="absolute right-2 bottom-2 text-xs text-(--dark5) select-none">
            {{ charCount }} char{{ charCount === 1 ? '' : 's' }}
          </div>

          <p v-if="touchedText && !validCharCount" class="text-sm text-red-400 mt-2" role="alert" aria-live="polite">
            Review must be between 20 and 200 characters (currently {{ charCount }}).
          </p>
        </div>

        <div class="flex justify-end gap-2">
          <button type="button" class="px-4 py-2 border rounded hover:bg-[var(--bg_highlight)]" @click="$emit('close')">Cancel</button>

          <button type="submit"
                  :disabled="!formValid"
                  :class="[
                    'px-4 py-2 rounded',
                    formValid ? 'bg-blue-600 text-white hover:bg-blue-700' : 'bg-[color:var(--color-border)]/30 text-[var(--fg)] cursor-not-allowed'
                  ]">
            Submit Review
          </button>
        </div>

        <div class="sr-only" aria-live="polite">
          <span v-if="!formValid">Form invalid: {{ !authorValid ? 'name required.' : '' }}{{ !validCharCount ? 'invalid character count.' : '' }}</span>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ref, computed } from 'vue'
  import StudySpot from '../classes/spot'
  import { ReviewShape } from '../classes/reviews'

  const props = defineProps<{
    spot: StudySpot | null
  }>()

  const emit = defineEmits<{
    (e: 'close'): void
    (e: 'submitted', review: ReviewShape): void
  }>()

  // stored username 
  const storedUsername = localStorage.getItem('username') || ''
  const usernamePresent = !!storedUsername

  // Author field prefilled with stored username if available
  const author = ref<string>(storedUsername || '')

  const rating = ref<number>(5)
  const text = ref<string>('')
  const today = new Date().toISOString().slice(0, 10)
  const date = ref<string>(today)

  const touchedAuthor = ref(false)
  const touchedText = ref(false)

  // submission error message
  const submitError = ref<string | null>(null)

  // character count helper
  const charCount = computed(() => text.value.length)

  const validCharCount = computed(() => charCount.value >= 20 && charCount.value <= 200)
  const authorValid = computed(() => {
    const v = author.value.trim()
    if (usernamePresent) return v === storedUsername
    return v.length > 0
  })

  const formValid = computed(() => authorValid.value && validCharCount.value)

  function setRating(n: number) {
    rating.value = n
  }

  function onTextInput() {
    // charCount computed updates automatically
    if (submitError.value) submitError.value = null
  }

  function submit() {
    touchedAuthor.value = true
    touchedText.value = true
    submitError.value = null

    if (!formValid.value) {
      // build helpful message
      const parts: string[] = []
      if (!authorValid.value) {
        parts.push(usernamePresent ? 'Name must match your username.' : 'Please enter your name.')
      }
      if (!validCharCount.value) {
        parts.push(`Review must be between 20 and 200 characters (currently ${charCount.value}).`)
      }
      submitError.value = parts.join(' ')
      return
    }

    if (!props.spot) return

    const review: ReviewShape = {
      spot_id: props.spot.id,
      author: author.value || 'anonymous',
      rating: Number(rating.value) || 5,
      text: text.value || '',
      date: date.value || today,
    }

    emit('submitted', review)
    emit('close')
  }
</script>
