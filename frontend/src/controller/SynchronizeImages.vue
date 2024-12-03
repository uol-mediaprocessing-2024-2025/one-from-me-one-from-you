<script setup>
import { ref } from 'vue'; // Import ref and lifecycle hooks
import axios from 'axios'; // Axios for API requests
import { store } from './store.js'; // Import the reactive store

const images = ref([]);

async function fetchAndStoreImages() {
  try {
    const response = await axios.get(`${store.apiUrl}/getImages`, {
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (response.status === 200 && Array.isArray(response.data.image_files)) {
      // Clear existing data in the store
      store.photoUrls = [];
      store.photoBlobs = [];

      // Populate the store with new image URLs and blobs
      for (const image of response.data.image_files) {
        const fullUrl = `${store.apiUrl}/uploaded_images/${image}`;
        store.photoUrls.push(fullUrl);

        // Fetch the image as a blob
        const blobResponse = await axios.get(fullUrl, { responseType: 'blob' });
        store.photoBlobs.push(blobResponse.data);

        console.log("Image URL and blob added to store:", fullUrl);
      }

      // Optionally update the local state for this component
      images.value = [...store.photoUrls];
    } else {
      console.error("No images found:", response.data.message);
    }
  } catch (error) {
    console.error("Error fetching images:", error);
  }
}
</script>

<template>
  <div>
    <h1>Fetched Images</h1>
    <div v-if="images.length">
      <ul>
        <li v-for="(image, index) in images" :key="index">
          <img :src="image" :alt="'Image ' + index" style="max-width: 200px;" />
        </li>
      </ul>
    </div>
    <p v-else>No images available.</p>
  </div>
</template>

<style scoped>

</style>