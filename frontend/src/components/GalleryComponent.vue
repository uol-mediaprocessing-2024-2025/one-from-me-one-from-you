<script setup>
import { ref } from 'vue'; // Import lifecycle hook and ref from Vue
import { store } from '../store'; // Import the global store to access shared state

// Reactive reference to hold the list of images and the modal state
const selectedImage = ref(null); // Track the currently selected image
const isModalOpen = ref(false); // Track whether the modal is open

const handleImageClick = (imageSrc) => {
  selectedImage.value = imageSrc;
  isModalOpen.value = true;
};

const closeModal = () => {
  isModalOpen.value = false;
  selectedImage.value = null;
};
</script>

<template>
  <div class="gallery px-4 py-4">
    <v-row dense>
      <v-col
        v-for="(imgSrc, index) in store.photoUrls"
        :key="index"
        class="d-flex child-flex"
        cols="12"
        sm="6"
        md="4"
        lg="3"
        xl="2">
        <v-img
          :src="imgSrc"
          aspect-ratio="1.67"
          class="mb-4 clickable-image"
          @click="handleImageClick(imgSrc)">
          <template v-slot:placeholder>
            <v-row align="center" class="fill-height ma-0" justify="center">
              <v-progress-circular color="grey-lighten-5" indeterminate></v-progress-circular>
            </v-row>
          </template>
        </v-img>
      </v-col>
    </v-row>
  </div>

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

.clickable-image{
  border: 1px dotted;
}
</style>
