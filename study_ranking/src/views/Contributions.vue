<template>
  <div class="p-6">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-3xl">Contributions</h1>
      <button v-if="username"
              @click="activeTab = 'submit'"
              class="px-6 py-2 rounded-md text-base text-center hover:cursor-pointer hover:bg-(--fg_gutter) border">
        + New Study Spot
      </button>
    </div>

    <div v-if="!username" class="p-4 border rounded bg-[var(--bg_highlight)]">
      <p class="text-[var(--dark5)]">You must be signed in to view your contributions.</p>
      <div class="mt-4">
        <button class="px-4 py-2 border rounded" @click="goToAccount">Sign in / Create account</button>
      </div>
    </div>

    <div v-else class="space-y-6">
      <!-- Tab Navigation -->
      <div class="flex gap-2 border-b pb-2">
        <button v-for="tab in tabs"
                :key="tab.id"
                @click="activeTab = tab.id"
                :class="[
            'px-4 py-2 rounded-t-lg transition-colors',
            activeTab === tab.id
              ? 'bg-(--cyan)/15 border-b-2 border-(--cyan)'
              : 'hover:bg-(--cyan)/5 hover:cursor-pointer'
          ]">
          {{ tab.label }}
          <span v-if="tab.count !== undefined" class=" text-sm px-1 py-1 rounded-md text-base text-center hover:cursor-pointer hover:bg-(--cyan)/25 bg-(--cyan)/10 border border-(--cyan) text-(--cyan)">
            {{ tab.count }}
          </span>
        </button>
      </div>

      <!-- Components for each tab -->
      <MySpots v-if="activeTab === 'submitted'"
               :spots="mySubmittedSpots"
               @edit-spot="editSpot"
               @view-spot="viewSpot"
               @delete-spot="deleteSpot"
               @switch-to-submit="activeTab = 'submit'" />

      <MyVotes v-else-if="activeTab === 'votes'"
               :votes="myVotes"
               :all-spots="allSpots" />

      <NewSpot v-else-if="activeTab === 'submit'"
               ref="newSpotRef"
               :error="submitError"
               :success="submitSuccess"
               @submit="submitNewSpot"
               @reset="resetForm" />
    </div>

    <!-- View Spot Details Modal -->
    <StudySpotDetails v-if="showViewModal && viewingSpot"
                      :spot="viewingSpot"
                      :initial-open-reviews="reviewsInitialOpen"
                      @close="closeViewModal" />

    <!-- Edit Spot Modal -->
    <div v-if="showEditModal && editingSpot"
         class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/30 backdrop-blur-custom"
         @click.self="closeEditModal">
      <div class="bg-[var(--bg)] rounded-xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div class="sticky top-0 bg-[var(--bg)] p-6 pb-4 border-b flex justify-between items-start z-10">
          <h2 class="text-2xl font-semibold">Edit Study Spot</h2>
          <button @click="closeEditModal"
                  class="text-xl font-bold cursor-pointer hover:text-red-500">
            ✕
          </button>
        </div>

        <div class="p-6 pt-4">
          <EditSpot ref="editSpotRef"
                    :spot="editingSpot"
                    :error="editError"
                    :success="editSuccess"
                    @submit="saveEditedSpot"
                    @cancel="closeEditModal" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
  import { useRouter } from 'vue-router'
  import StudySpot from '@/classes/spot'
  import { voteCategories } from '@/classes/categories'
  import { getVotesForSpot } from '@/data/votesMap'
  import MySpots from '@/components/MySpots.vue'
  import NewSpot from '@/components/NewSpot.vue'
  import EditSpot from '@/components/EditSpot.vue'
  import MyVotes from '@/components/MyVotes.vue'
  import StudySpotDetails from '@/components/StudySpotDetails.vue'
  import { deleteReviewsForSpot, primeReviewsForSpots } from '@/data/reviewsMap'
  import { deleteVotesForSpot, loadUserVotesFromBackend, setStudentId } from '@/data/votesMap'
  import type { Vote } from '@/components/MyVotes.vue'
  import { apiPost, deleteSpot as deleteSpotApi, updateSpot as updateSpotApi, fetchSpotsForUser } from '@/api'
  import { fetchAndStoreSpots, mapApiSpot } from '@/data/spotsMap'

  const router = useRouter()
  const username = ref<string | null>(null)
  const studentId = ref<number | null>(null)
  const activeTab = ref<'submit' | 'submitted' | 'votes'>('submitted')
  const newSpotRef = ref<InstanceType<typeof NewSpot> | null>(null)
  const editSpotRef = ref<InstanceType<typeof EditSpot> | null>(null)

  // View modal state
  const showViewModal = ref(false)
  const viewingSpot = ref<StudySpot | null>(null)
  const reviewsInitialOpen = ref(false)

  // Edit modal state
  const showEditModal = ref(false)
  const editingSpot = ref<StudySpot | null>(null)
  const editError = ref('')
  const editSuccess = ref('')

  // Form state
  const submitError = ref('')
  const submitSuccess = ref('')

  // Data
  const allSpots = ref<StudySpot[]>([])
  const userSpots = ref<StudySpot[]>([])
  const userBackendVotes = ref<Record<number, any[]>>({})
  const isLoadingSpots = ref(false)

  // Computed
  const mySubmittedSpots = computed(() => userSpots.value)

  const myVotes = computed((): Vote[] => {
    if (!studentId.value) return []

    const votes: Vote[] = []

    // Get votes from backend
    const allUserVotes = Object.values(userBackendVotes.value).flat()

    allUserVotes.forEach(vote => {
      const spot = allSpots.value.find(s => s.id === vote.spot_id)
      if (spot) {
        // Convert rating to direction: 1-2 = downvote (-1), 4-5 = upvote (1)
        const direction = vote.rating >= 4 ? 1 : -1

        votes.push({
          spotId: vote.spot_id,
          spotName: spot.name,
          category: vote.slug,
          categoryLabel: vote.display_name,
          categoryDesc: voteCategories.find(c => c.key === vote.slug)?.desc || '',
          direction: direction as 1 | -1
        })
      }
    })

    return votes
  })

  const tabs = computed(() => [
    { id: 'submitted' as const, label: 'My Spots', count: mySubmittedSpots.value.length },
    { id: 'votes' as const, label: 'My Votes', count: myVotes.value.length },
    { id: 'submit' as const, label: 'Submit New' }
  ])

  // Functions
  function loadUsername() {
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      try {
        const parsed = JSON.parse(storedUser)
        username.value = parsed?.netid || localStorage.getItem('username')
        studentId.value = parsed?.student_id || null
        return
      } catch {
        // fall through
      }
    }
    username.value = localStorage.getItem('username')
  }

  async function loadUserVotes() {
    if (!studentId.value) {
      userBackendVotes.value = {}
      return
    }

    try {
      setStudentId(studentId.value)
      const votes = await loadUserVotesFromBackend(studentId.value)
      userBackendVotes.value = votes
    } catch (error) {
      console.error('Failed to load user votes from backend:', error)
      userBackendVotes.value = {}
    }
  }

  async function loadUserSubmittedSpots() {
    if (!studentId.value) {
      userSpots.value = []
      return
    }

    try {
      const spots = await fetchSpotsForUser(studentId.value)
      userSpots.value = Array.isArray(spots) ? spots.map(mapApiSpot) : []
    } catch (err) {
      console.error('Failed to load user spots:', err)
      userSpots.value = []
    }
  }

  async function loadStudySpots() {
    isLoadingSpots.value = true
    try {
      const spots = await fetchAndStoreSpots()
      allSpots.value = spots
      primeReviewsForSpots(spots.map(s => s.id)).catch(() => {})
    } catch (err) {
      console.error('Failed to load study spots from backend:', err)
      allSpots.value = []
    } finally {
      isLoadingSpots.value = false
    }
  }

  function goToAccount() {
    router.push({ path: '/', query: { showAccount: 'true' } })
  }

  function viewSpot(spot: StudySpot) {
    viewingSpot.value = spot
    reviewsInitialOpen.value = false
    showViewModal.value = true
  }

  function closeViewModal() {
    showViewModal.value = false
    viewingSpot.value = null
    reviewsInitialOpen.value = false
  }

  async function deleteSpot(spot: StudySpot) {
    try {
      if (spot.id) await deleteSpotApi(spot.id)

      allSpots.value = allSpots.value.filter(s => s.id !== spot.id)
      localStorage.setItem('studySpots', JSON.stringify(allSpots.value))
      userSpots.value = userSpots.value.filter(s => s.id !== spot.id)

      deleteReviewsForSpot(spot.id)
      deleteVotesForSpot(spot.id)

      window.dispatchEvent(new CustomEvent('spots-changed'))

      await loadStudySpots()
    } catch (error) {
      console.error('Failed to delete spot:', error)
    }
  }

  async function submitNewSpot(data: {
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
  }) {
    submitError.value = ''
    submitSuccess.value = ''

    if (!username.value) {
      submitError.value = 'Please sign in to submit a study spot.'
      return
    }

    try {
      const payload = {
        name: data.name.trim(),
        building_code: data.building_code.trim().toUpperCase(),
        area_description: (data.area_description || data.description || '').trim() || null,
        seating_capacity: Math.max(0, Number(data.seating_capacity) || 0),
        power_outlets: !!data.power_outlets,
        natural_light: !!data.natural_light,
        open_24_7: !!data.open_24_7,
        is_active: true,
        student_id: studentId.value
      }

      const created = await apiPost('/spots', payload)
      const mapped = mapApiSpot(created)
      allSpots.value = [mapped, ...allSpots.value]
      localStorage.setItem('studySpots', JSON.stringify(allSpots.value))
      if (mapped.id) userSpots.value = [mapped, ...userSpots.value]

      submitSuccess.value = 'Study spot submitted successfully!'
      if (newSpotRef.value) {
        newSpotRef.value.setSuccess('Study spot submitted successfully!')
      }

      setTimeout(() => {
        activeTab.value = 'submitted'
        submitSuccess.value = ''
      }, 1500)
    } catch (error) {
      console.error('Failed to submit study spot:', error)
      submitError.value = 'Failed to submit study spot. Please try again.'
      if (newSpotRef.value) {
        newSpotRef.value.setError('Failed to submit study spot. Please try again.')
      }
    }
  }

  function resetForm() {
    submitError.value = ''
    submitSuccess.value = ''
  }

  function editSpot(spot: StudySpot) {
    editingSpot.value = new StudySpot(
      spot.name,
      spot.description,
      spot.id,
      spot.creator_id,
      spot.rating,
      spot.building_code,
      spot.area_description,
      spot.seating_capacity,
      spot.power_outlets,
      spot.natural_light,
      spot.open_24_7,
      spot.is_active,
      [...spot.categories]
    )
    showEditModal.value = true
    editError.value = ''
    editSuccess.value = ''
  }

  function closeEditModal() {
    showEditModal.value = false
    editingSpot.value = null
    editError.value = ''
    editSuccess.value = ''
  }

  async function saveEditedSpot(data: {
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
  }) {
    editError.value = ''
    editSuccess.value = ''

    try {
      const idx = allSpots.value.findIndex(s => s.id === data.id)
      if (idx > -1) {
        const payload = {
          name: data.name.trim(),
          building_code: data.building_code.trim().toUpperCase(),
          area_description: (data.area_description || data.description || '').trim() || null,
          seating_capacity: Math.max(0, Number(data.seating_capacity) || 0),
          power_outlets: !!data.power_outlets,
          natural_light: !!data.natural_light,
          open_24_7: !!data.open_24_7,
        }

        const updatedFromApi = await updateSpotApi(data.id, payload)
        const updatedMapped = mapApiSpot(updatedFromApi)
        const updatedSpot = new StudySpot(
          updatedMapped.name,
          updatedMapped.description,
          updatedMapped.id,
          allSpots.value[idx].creator_id,
          updatedMapped.rating,
          updatedMapped.building_code,
          updatedMapped.area_description,
          updatedMapped.seating_capacity,
          updatedMapped.power_outlets,
          updatedMapped.natural_light,
          updatedMapped.open_24_7,
          updatedMapped.is_active,
          updatedMapped.categories
        )

        allSpots.value[idx] = updatedSpot
        localStorage.setItem('studySpots', JSON.stringify(allSpots.value))

        const userIdx = userSpots.value.findIndex(s => s.id === data.id)
        if (userIdx > -1) userSpots.value[userIdx] = updatedSpot

        editSuccess.value = 'Changes saved successfully!'
        if (editSpotRef.value) {
          editSpotRef.value.setSuccess('Changes saved successfully!')
        }

        setTimeout(() => {
          closeEditModal()
        }, 1000)
      }
    } catch (error) {
      console.error('Failed to save spot:', error)
      editError.value = 'Failed to save changes. Please try again.'
      if (editSpotRef.value) {
        editSpotRef.value.setError('Failed to save changes. Please try again.')
      }
    }
  }

  function onAccountChanged(e: Event) {
    const evt = e as CustomEvent
    const userObj = evt.detail
    if (userObj) {
      username.value = userObj?.netid || userObj?.username
      studentId.value = userObj?.student_id || null
    } else {
      username.value = null
      studentId.value = null
    }
    loadUserSubmittedSpots()
    loadUserVotes()
  }

  onMounted(() => {
    loadUsername()
    loadStudySpots()
    loadUserSubmittedSpots()
    loadUserVotes()
    window.addEventListener('account-changed', onAccountChanged)
  })

  onBeforeUnmount(() => {
    window.removeEventListener('account-changed', onAccountChanged)
  })
</script>
