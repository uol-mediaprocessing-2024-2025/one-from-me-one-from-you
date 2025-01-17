// Import Vue Router components and views
import { createRouter, createWebHistory } from 'vue-router'
import GalleryView from '../views/GalleryView.vue'
import MainView from '../views/MainView.vue'
import UploadImageView from '../views/UploadImageView.vue'

// Create and configure the router
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL), // Use HTML5 history mode for clean URLs
  routes: [
    {
      path: '/',
      name: 'main',
      component: MainView
    },
    {
      path: '/gallery',
      name: 'gallery',
      component: GalleryView
    },
    {
      path: '/uploadImage',
      name: 'uploadImage',
      component: UploadImageView
    }
  ]
})

// Export the router for use in the Vue app
export default router
