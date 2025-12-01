<template>
  <div class="space-y-4">
    <div class="bg-[var(--bg_highlight)] p-6 rounded-lg border">
      <form @submit.prevent="handleSubmit" class="space-y-4" novalidate>
        <!-- Basic Information -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium mb-2">Spot Name *</label>
            <input v-model="formData.name"
                   type="text"
                   placeholder="e.g., Library 3rd Floor"
                   :class="[
                     'w-full px-3 py-2 rounded border bg-[var(--bg)] focus:outline-none focus:ring-2',
                     fieldErrors.name ? 'border-red-500 focus:ring-red-500' : 'focus:ring-blue-600'
                   ]" />
            <p v-if="fieldErrors.name" class="text-red-500 text-xs mt-1">{{ fieldErrors.name }}</p>
          </div>

          <div>
            <label class="block text-sm font-medium mb-2">Building Code *</label>
            <input v-model="formData.building_code"
                   type="text"
                   placeholder="e.g., LIB"
                   :class="[
                     'w-full px-3 py-2 rounded border bg-[var(--bg)] focus:outline-none focus:ring-2',
                     fieldErrors.building_code ? 'border-red-500 focus:ring-red-500' : 'focus:ring-blue-600'
                   ]" />
            <p v-if="fieldErrors.building_code" class="text-red-500 text-xs mt-1">{{ fieldErrors.building_code }}</p>
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium mb-2">Description *</label>
          <textarea v-model="formData.description"
                    rows="3"
                    placeholder="Describe the study spot..."
                    :class="[
                      'w-full px-3 py-2 rounded border bg-[var(--bg)] focus:outline-none focus:ring-2',
                      fieldErrors.description ? 'border-red-500 focus:ring-red-500' : 'focus:ring-blue-600'
                    ]"></textarea>
          <p v-if="fieldErrors.description" class="text-red-500 text-xs mt-1">{{ fieldErrors.description }}</p>
        </div>

        <div>
          <label class="block text-sm font-medium mb-2">Area Description *</label>
          <input v-model="formData.area_description"
                 type="text"
                 placeholder="e.g., Near the windows, quiet section"
                 :class="[
                   'w-full px-3 py-2 rounded border bg-[var(--bg)] focus:outline-none focus:ring-2',
                   fieldErrors.area_description ? 'border-red-500 focus:ring-red-500' : 'focus:ring-blue-600'
                 ]" />
          <p v-if="fieldErrors.area_description" class="text-red-500 text-xs mt-1">{{ fieldErrors.area_description }}</p>
        </div>

        <!-- Rating -->
        <div>
          <label class="block text-sm font-medium mb-2">Rating *</label>
          <div class="flex items-center gap-2">
            <button v-for="star in 5"
                    :key="star"
                    type="button"
                    @click="formData.rating = star"
                    :class="[
                    'text-3xl transition-colors' ,
                    star <= formData.rating ? 'text-yellow-500' : 'text-gray-400',
                      'hover:text-yellow-400'
                    ]">
              ★
            </button>
            <span v-if="formData.rating > 0" class="ml-2 text-sm text-[var(--dark5)]">
              {{ formData.rating }} / 5
            </span>
          </div>
          <p v-if="fieldErrors.rating" class="text-red-500 text-xs mt-1">{{ fieldErrors.rating }}</p>
        </div>

        <!-- Details -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium mb-2">Seating Capacity *</label>
            <input v-model.number="formData.seating_capacity"
                   type="number"
                   min="0"
                   placeholder="Number of seats"
                   :class="[
                     'w-full px-3 py-2 rounded border bg-[var(--bg)] focus:outline-none focus:ring-2',
                     fieldErrors.seating_capacity ? 'border-red-500 focus:ring-red-500' : 'focus:ring-blue-600'
                   ]" />
            <p v-if="fieldErrors.seating_capacity" class="text-red-500 text-xs mt-1">{{ fieldErrors.seating_capacity }}</p>
          </div>
        </div>

        <!-- Amenities -->
        <div class="space-y-2">
          <label class="block text-sm font-medium mb-2">Amenities</label>
          <div class="flex flex-wrap gap-4">
            <label class="flex items-center gap-2 cursor-pointer">
              <input v-model="formData.power_outlets" type="checkbox" class="rounded" />
              <span class="text-sm">Power Outlets</span>
            </label>
            <label class="flex items-center gap-2 cursor-pointer">
              <input v-model="formData.natural_light" type="checkbox" class="rounded" />
              <span class="text-sm">Natural Light</span>
            </label>
            <label class="flex items-center gap-2 cursor-pointer">
              <input v-model="formData.open_24_7" type="checkbox" class="rounded" />
              <span class="text-sm">Open 24/7</span>
            </label>
          </div>
        </div>

        <!-- Categories -->
        <div>
          <label class="block text-sm font-medium mb-2">Categories (Maximum 4)</label>
          <p class="text-xs text-[var(--dark5)] mb-3">Add custom categories to describe this study spot</p>

          <!-- Input for adding new categories -->
          <div class="flex gap-2 mb-3">
            <input v-model="newCategoryInput"
                   type="text"
                   placeholder="Type a category (e.g., Quiet, Group Study)..."
                   @keydown.enter.prevent="addCategory"
                   :disabled="formData.categories.length >= 4"
                   class="flex-1 px-3 py-2 rounded border bg-[var(--bg)] focus:outline-none focus:ring-2 focus:ring-blue-600 disabled:opacity-50 disabled:cursor-not-allowed" />
            <button type="button"
                    @click="addCategory"
                    :disabled="!newCategoryInput.trim() || formData.categories.length >= 4"
                    class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
              Add
            </button>
          </div>

          <!-- Display added categories -->
          <div v-if="formData.categories.length > 0" class="flex flex-wrap gap-2">
            <span v-for="(cat, index) in formData.categories"
                  :key="index"
                  class="px-3 py-1 rounded-full text-sm bg-blue-600 text-white flex items-center gap-2">
              {{ cat }}
              <button type="button"
                      @click="removeCategory(index)"
                      class="hover:text-red-200 transition-colors font-bold"
                      title="Remove category">
                ✕
              </button>
            </span>
          </div>
          <div v-else class="text-xs text-[var(--dark5)] italic">
            No categories added yet. Add some to help others find this spot!
          </div>
          <p v-if="formData.categories.length >= 4" class="text-xs text-yellow-600 mt-2">
            Maximum of 4 categories reached
          </p>
        </div>

        <div v-if="error" class="text-red-500 text-sm">{{ error }}</div>
        <div v-if="success" class="text-green-500 text-sm">{{ success }}</div>

        <div class="flex gap-3 pt-4">
          <button type="submit"
                  class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            Save Changes
          </button>
          <button type="button"
                  @click="handleCancel"
                  class="px-4 py-2 bg-[var(--bg)] border rounded hover:bg-gray-700/20">
            Cancel
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ref, watch } from 'vue'
  import type StudySpot from '@/classes/spot'

  const props = defineProps<{
    spot: StudySpot | null
    error?: string
    success?: string
  }>()

  const emit = defineEmits<{
    (e: 'submit', data: {
      id: number
      name: string
      description: string
      building_code: string
      area_description: string
      rating: number
      seating_capacity: number
      power_outlets: boolean
      natural_light: boolean
      open_24_7: boolean
      categories: string[]
    }): void
    (e: 'cancel'): void
  }>()

  const formData = ref({
    id: 0,
    name: '',
    description: '',
    building_code: '',
    area_description: '',
    rating: 0,
    seating_capacity: 0,
    power_outlets: false,
    natural_light: false,
    open_24_7: false,
    categories: [] as string[]
  })

  const fieldErrors = ref({
    name: '',
    description: '',
    building_code: '',
    area_description: '',
    rating: '',
    seating_capacity: ''
  })

  const newCategoryInput = ref('')
  const error = ref(props.error || '')
  const success = ref(props.success || '')

  // Watch for spot prop changes and populate form
  watch(() => props.spot, (newSpot) => {
    if (newSpot) {
      formData.value = {
        id: newSpot.id,
        name: newSpot.name,
        description: newSpot.description,
        building_code: newSpot.building_code,
        area_description: newSpot.area_description,
        rating: newSpot.rating,
        seating_capacity: newSpot.seating_capacity,
        power_outlets: newSpot.power_outlets,
        natural_light: newSpot.natural_light,
        open_24_7: newSpot.open_24_7,
        categories: [...newSpot.categories]
      }
    }
  }, { immediate: true })

  function validateFields(): boolean {
    let isValid = true

    // Clear previous errors
    fieldErrors.value = {
      name: '',
      description: '',
      building_code: '',
      area_description: '',
      rating: '',
      seating_capacity: ''
    }

    // Validate spot name
    if (!formData.value.name.trim()) {
      fieldErrors.value.name = 'Please fill out this field'
      isValid = false
    }

    // Validate building code
    if (!formData.value.building_code.trim()) {
      fieldErrors.value.building_code = 'Please fill out this field'
      isValid = false
    }

    // Validate description
    if (!formData.value.description.trim()) {
      fieldErrors.value.description = 'Please fill out this field'
      isValid = false
    }

    // Validate area description
    if (!formData.value.area_description.trim()) {
      fieldErrors.value.area_description = 'Please fill out this field'
      isValid = false
    }

    // Validate rating
    if (formData.value.rating === 0) {
      fieldErrors.value.rating = 'Please select a rating'
      isValid = false
    }

    // Validate seating capacity
    if (formData.value.seating_capacity === 0 || formData.value.seating_capacity < 0) {
      fieldErrors.value.seating_capacity = 'Please enter a valid seating capacity'
      isValid = false
    }

    return isValid
  }

  function addCategory() {
    const category = newCategoryInput.value.trim()

    if (!category) {
      return
    }

    // Check if maximum categories reached
    if (formData.value.categories.length >= 4) {
      error.value = 'Maximum of 4 categories allowed.'
      setTimeout(() => { error.value = '' }, 3000)
      return
    }

    // Check for duplicates (case-insensitive)
    const exists = formData.value.categories.some(
      cat => cat.toLowerCase() === category.toLowerCase()
    )

    if (exists) {
      error.value = 'This category has already been added.'
      setTimeout(() => { error.value = '' }, 3000)
      return
    }

    // Capitalize first letter of each word
    const formatted = category
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ')

    formData.value.categories.push(formatted)
    newCategoryInput.value = ''
    error.value = ''
  }

  function removeCategory(index: number) {
    formData.value.categories.splice(index, 1)
  }

  function handleSubmit() {
    error.value = ''
    success.value = ''

    if (!validateFields()) {
      return
    }

    emit('submit', { ...formData.value })
  }

  function handleCancel() {
    emit('cancel')
  }

  function resetForm() {
    if (props.spot) {
      formData.value = {
        id: props.spot.id,
        name: props.spot.name,
        description: props.spot.description,
        building_code: props.spot.building_code,
        area_description: props.spot.area_description,
        rating: props.spot.rating,
        seating_capacity: props.spot.seating_capacity,
        power_outlets: props.spot.power_outlets,
        natural_light: props.spot.natural_light,
        open_24_7: props.spot.open_24_7,
        categories: [...props.spot.categories]
      }
    }
    fieldErrors.value = {
      name: '',
      description: '',
      building_code: '',
      area_description: '',
      rating: '',
      seating_capacity: ''
    }
    newCategoryInput.value = ''
    error.value = ''
    success.value = ''
  }

  defineExpose({
    resetForm,
    setError: (msg: string) => { error.value = msg },
    setSuccess: (msg: string) => { success.value = msg }
  })
</script>
