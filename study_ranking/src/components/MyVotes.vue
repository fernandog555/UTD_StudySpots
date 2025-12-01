<template>
  <div class="space-y-4">
    <div class="bg-[var(--bg_highlight)] p-4 rounded-lg border">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-2xl font-semibold">My Vote Contributions</h2>

        <Filter v-if="votes.length > 0"
                v-model="selectedFilter"
                :options="filterOptions"
                id="vote-filter"
                label="Filter votes" />
      </div>

      <div v-if="votes.length === 0" class="text-[var(--dark5)] text-center py-8">
        <p>You haven't cast any votes yet.</p>
        <p class="text-sm mt-2">Visit study spots and vote on their categories to help the community!</p>
      </div>

      <div v-else class="space-y-3">
        <div v-for="vote in sortedVotes"
             :key="`${vote.spotId}-${vote.category}`"
             class="p-4 border rounded bg-[var(--bg)]">
          <div class="flex justify-between items-start">
            <div class="flex-1">
              <h3 class="text-xl font-semibold">{{ vote.spotName }}</h3>
              <div class="flex items-center gap-2 mt-2">
                <span class="px-2 py-1 rounded-md text-base text-center bg-(--cyan)/10 border border-(--cyan) text-(--cyan)">
                  {{ vote.categoryLabel }}
                </span>
                <span :class="[
                    'text-lg font-bold',
                    vote.direction === 1 ? 'text-(--green)' : 'text-(--red1)'
                  ]">
                  {{ vote.direction === 1 ? '▲ Upvote' : '▼ Downvote' }}
                </span>
              </div>
              <p class="text-xs text-[var(--dark5)] mt-1">{{ vote.categoryDesc }}</p>
            </div>
            <button @click="openVotesModal(vote.spotId)"
                    class="px-6 py-2 rounded-md text-base text-center hover:cursor-pointer hover:bg-(--fg_gutter) border">
              View Spot
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Votes Modal -->
    <Votes v-model:visible="showVotesModal"
           :spot="selectedSpotForVoting"
           @require-auth="handleRequireAuth" />

    <!-- Auth Modal -->
    <Auth v-model="showAuthModal"
          title="Account Needed"
          message="You need an account to vote on study spots. Create an account or sign in to cast a vote."
          @confirm="goToAccount"
          @cancel="showAuthModal = false" />
  </div>
</template>

<script setup lang="ts">
  import { ref, computed } from 'vue'
  import { useRouter } from 'vue-router'
  import Filter from './Filter.vue'
  import Votes from './Votes.vue'
  import Auth from '../views/Auth.vue'
  import type StudySpot from '@/classes/spot'

  export interface Vote {
    spotId: number
    spotName: string
    category: string
    categoryLabel: string
    categoryDesc: string
    direction: 1 | -1
  }

  const props = defineProps<{
    votes: Vote[]
    allSpots: StudySpot[]
  }>()

  const router = useRouter()
  const selectedFilter = ref('upvote-asc')
  const showVotesModal = ref(false)
  const showAuthModal = ref(false)
  const selectedSpotForVoting = ref<StudySpot | null>(null)

  const filterOptions = [
    { value: 'upvote-asc', label: 'Upvotes' },
    { value: 'downvote-asc', label: 'Downvotes' },
    { value: 'alpha-asc', label: 'Alphabetical ↑' },
    { value: 'alpha-desc', label: 'Alphabetical ↓' }
  ]

  const sortedVotes = computed(() => {
    const votesCopy = [...props.votes]

    switch (selectedFilter.value) {
      case 'upvote-asc':
        return votesCopy.sort((a, b) => b.direction - a.direction || a.spotName.localeCompare(b.spotName))

      case 'downvote-asc':
        return votesCopy.sort((a, b) => a.direction - b.direction || a.spotName.localeCompare(b.spotName))

      case 'alpha-asc':
        return votesCopy.sort((a, b) => a.spotName.localeCompare(b.spotName))

      case 'alpha-desc':
        return votesCopy.sort((a, b) => b.spotName.localeCompare(a.spotName))

      default:
        return votesCopy
    }
  })

  function openVotesModal(spotId: number) {
    const spot = props.allSpots.find(s => s.id === spotId)
    if (spot) {
      selectedSpotForVoting.value = spot
      showVotesModal.value = true
    }
  }

  function handleRequireAuth() {
    showVotesModal.value = false
    showAuthModal.value = true
  }

  function goToAccount() {
    showAuthModal.value = false
    router.push({ path: '/', query: { showAccount: 'true' } })
  }
</script>
