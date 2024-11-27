<script setup>
import { onMounted, ref } from 'vue'; // Import lifecycle hook and ref from Vue
import { store } from '../store'; // Import the global store to access shared state

// Reactive reference to hold the list of images and the modal state
const images = ref([]);
const selectedImage = ref(null); // Track the currently selected image
const isModalOpen = ref(false); // Track whether the modal is open

// onMounted lifecycle hook to fetch images when the component is mounted
onMounted(() => {
  images.value = store.photoUrls;
});

// Function to handle image click and set the selected image for the modal
const handleImageClick = (imageSrc) => {
  selectedImage.value = imageSrc; // Set the selected image
  isModalOpen.value = true; // Open the modal
};

// Function to close the modal
const closeModal = () => {
  isModalOpen.value = false; // Close the modal
  selectedImage.value = null; // Clear the selected image
};
</script>

<template>
  <!-- Gallery container -->
  <div class="gallery px-4 py-4">
    <!-- Vuetify grid to organize images -->
    <v-row dense>
      <!-- Loop through the images array and display each image -->
      <v-col
        v-for="(imgSrc, index) in images"
        :key="index"
        class="d-flex child-flex"
        cols="12"
        sm="6"
        md="4"
        lg="3"
        xl="2"
      >
        <!-- Display each image with Vuetify's v-img component -->
        <v-img
          :src="imgSrc"
          aspect-ratio="1.67"
          class="mb-4 clickable-image"
          @click="handleImageClick(imgSrc)"
        >
          <!-- Show a loading spinner while the image is loading -->
          <template v-slot:placeholder>
            <v-row align="center" class="fill-height ma-0" justify="center">
              <v-progress-circular color="grey-lighten-5" indeterminate></v-progress-circular>
            </v-row>
          </template>
        </v-img>
      </v-col>
    </v-row>
  </div>

  <!-- Modal for Enlarged Image -->
  <v-dialog v-model="isModalOpen" max-width="90vw">
    <v-card>
      <v-img :src="selectedImage" class="enlarged-image" contain />
      <v-btn icon @click="closeModal" class="close-btn">
        <v-icon>mdi-close</v-icon>
      </v-btn>
    </v-card>
  </v-dialog>
</template>

<style scoped>
.gallery {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
}

.v-img {
  border-radius: 12px;
  cursor: pointer;
  transition: transform 0.3s ease-in-out;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.v-img:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
}

.enlarged-image {
  max-width: 100%;
  max-height: 80vh;
  object-fit: contain;
}

.close-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: rgba(0, 0, 0, 0.5);
  color: white;
  border-radius: 50%;
}
</style>
