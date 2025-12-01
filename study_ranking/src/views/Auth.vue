<template>
  <div v-if="modelValue" class="fixed inset-0 z-50 flex items-center justify-center" @click.stop>
    <div class="absolute inset-0 bg-black/50 backdrop-blur-custom" @click="onCancel"></div>

    <div class="relative bg-(--bg) rounded-xl shadow-xl w-full max-w-md p-6 z-10">
      <button class="absolute top-3 right-3 text-xl font-bold cursor-pointer hover:text-red-500" @click="onCancel">
        ✕
      </button>

      <h3 class="text-xl font-semibold mb-2">{{ title }}</h3>
      <p class="mb-4 text-(--dark5)">{{ message }}</p>

      <div class="flex gap-3 justify-end mt-4">
        <button class="px-4 py-2 border rounded hover:bg-(--bg_highlight)" @click="onCancel">Cancel</button>
        <button class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700" @click="onConfirm">Sign In / Sign Up</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { defineProps, defineEmits, onMounted, onBeforeUnmount } from 'vue'

  const props = defineProps<{
    modelValue: boolean
    title?: string
    message?: string
  }>()

  const emit = defineEmits<{
    (e: 'update:modelValue', value: boolean): void
    (e: 'confirm'): void
    (e: 'cancel'): void
  }>()

  function onCancel() {
    emit('update:modelValue', false)
    emit('cancel')
  }

  function onConfirm() {
    emit('update:modelValue', false)
    emit('confirm')
  }

  function handleKeyDown(e: KeyboardEvent) {
    if (e.key === 'Escape' && props.modelValue) {
      onCancel()
    }
  }

  onMounted(() => {
    window.addEventListener('keydown', handleKeyDown)
  })

  onBeforeUnmount(() => {
    window.removeEventListener('keydown', handleKeyDown)
  })
</script>
