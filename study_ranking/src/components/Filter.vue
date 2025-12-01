<template>
  <div>
    <label v-if="label" :for="id" class="sr-only">{{ label }}</label>
    <select :id="id"
            :class="selectClass"
            :value="modelValue"
            @change="$emit('update:modelValue', $event.target.value)"
            aria-label="Filter options">
      <option v-for="opt in options" :key="opt.value" :value="opt.value">
        {{ opt.label }}
      </option>
    </select>
  </div>
</template>

<script setup lang="ts">import { PropType } from 'vue'

const props = defineProps({
  modelValue: { type: String, required: true },
  options: {
    type: Array as PropType<Array<{ value: string; label: string }>>,
    required: true
  },
  id: { type: String, default: undefined },
  label: { type: String, default: 'Filter' },
  selectClass: { type: String, default: "px-6 py-2 rounded-md text-base text-center hover:cursor-pointer hover:bg-(--fg_gutter) border" }
})
const emit = defineEmits<{
  (e: 'update:modelValue', v: string): void
}>()
</script>
