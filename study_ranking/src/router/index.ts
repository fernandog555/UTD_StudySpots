import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/HomeView.vue'
import SearchResults from '@/views/SearchResults.vue'
import StudySpotDetails from '@/components/StudySpotDetails.vue'
import BookmarkedSpots from '@/views/BookmarkedSpots.vue'
import MyReviews from '@/views/MyReviews.vue'
import Contributions from '@/views/Contributions.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/search/:query?',
      name: 'search',
      component: SearchResults,
    },
    {
      path: '/spot/:id',
      name: 'spot-details',
      component: StudySpotDetails,
    },
    {
      path: '/bookmarks',
      name: 'bookmarks',
      component: BookmarkedSpots,
    },
    {
      path: '/my-reviews',
      name: 'my-reviews',
      component: MyReviews,
    },
    {
      path: '/contributions',
      name: 'contributions',
      component: Contributions,
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'home',
      component: HomeView,
    },
  ],
})

export default router
