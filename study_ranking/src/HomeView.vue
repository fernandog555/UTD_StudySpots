<script setup lang="ts">
  import { useRoute } from 'vue-router'
  import router from './router'
  import { ref, watch } from 'vue'
  import Account from './components/Account.vue'
  import StudySpot from './classes/spot'

  const route = useRoute()

  // Keep a small reactive mode to pass into AccountModal when route opens it.
  const mode = ref<'login' | 'create'>('login')

  function setModeFromRoute() {
    const seg = route.fullPath.split('/')[1]
    if (seg === 'create') mode.value = 'create'
    else mode.value = 'login'
  }

  // ensure initial mode and keep in sync
  setModeFromRoute()
  watch(() => route.fullPath, () => {
    setModeFromRoute()
  })
</script>

<template>
  <!-- Account Modal  -->
  <Account v-if="route.fullPath.split('/')[1] === 'account'"
           :initialMode="mode"
           @close="router.push('/')" />

  <!-- Main Content -->
  <div class="p-4 sm:p-6 lg:p-8 text-base sm:text-lg leading-relaxed grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6 lg:gap-8">
    <div class="col-span-1 lg:col-span-2 border rounded-md p-4 sm:p-6 bg-(--bg_highlight)">
      <h1 class="text-2xl sm:text-3xl lg:text-4xl font-bold mb-3 sm:mb-4 text-(--blue) text-center">Welcome to Study Spots @ UTD</h1>
      <p class="mb-3 sm:mb-4 text-sm sm:text-base">
        Tired of wandering around campus looking for the perfect place to study? Whether you're cramming for finals,
        collaborating on a group project, or just need a quiet corner to recharge, <strong>Study Spots @ UTD</strong>
        is here to help. This web app is built by students, for students — making it easier than ever to find your ideal study
        environment at The University of Texas at Dallas.
      </p>
    </div>

    <div class="col-span-1 border rounded-md p-4 sm:p-6 bg-(--bg_highlight)">
      <h2 class="text-xl sm:text-2xl font-semibold mt-2 sm:mt-4 lg:mt-6 mb-2">Search & Discover</h2>
      <p class="mb-3 sm:mb-4 text-sm sm:text-base">
        Use the search bar above to explore study spots by name, keyword, or category. Discover hidden gems and popular
        locations like <em>ECSW</em>, <em>McDermott Library</em>, and the <em>Student Union</em>. Each spot includes a detailed
        description, real-time ratings, and honest feedback from fellow Comets.
      </p>
    </div>

    <div class="col-span-1 border rounded-md p-4 sm:p-6 bg-(--bg_highlight)">
      <h2 class="text-xl sm:text-2xl font-semibold mt-2 sm:mt-4 lg:mt-6 mb-2">Rate & Vote</h2>
      <p class="mb-3 sm:mb-4 text-sm sm:text-base">
        Your opinion matters! Rate study spots based on key criteria like <strong>quietness</strong>, <strong>comfort</strong>,
        <strong>Wi-Fi quality</strong>, and more. Upvote your favorites or downvote spots that didn't meet your expectations.
        These ratings help build a smarter, more personalized study experience for everyone.
      </p>
    </div>

    <div class="col-span-1 lg:col-span-2 border rounded-md p-4 sm:p-6 bg-(--bg_highlight)">
      <h2 class="text-xl sm:text-2xl font-semibold mt-2 sm:mt-4 lg:mt-6 mb-2">Create an Account</h2>
      <p class="mb-3 sm:mb-4 text-sm sm:text-base">
        Want to do more than just browse? Create an account to unlock full features: submit new study spots, leave detailed reviews,
        and bookmark your go-to locations. Your contributions help keep the platform fresh and relevant for the entire UTD community.
      </p>
    </div>

    <div class="col-span-1 lg:col-span-2 border rounded-md p-4 sm:p-6 bg-(--bg_highlight)">
      <h2 class="text-xl sm:text-2xl font-semibold mt-2 sm:mt-4 lg:mt-6 mb-2">Get Started</h2>
      <p class="text-sm sm:text-base">
        Ready to level up your study game? Click the Home button to return here anytime. Use the search bar to begin exploring,
        or log in to start contributing. Let's make studying at UTD smarter, more social, and way more efficient.
      </p>
    </div>
  </div>
</template>
