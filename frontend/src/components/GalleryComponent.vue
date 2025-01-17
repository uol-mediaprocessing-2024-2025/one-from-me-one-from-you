<script setup>
import { ref } from 'vue';
import { store } from '../store';
import { useRouter } from 'vue-router'; // To navigate programmatically

const router = useRouter(); // Initialize the router

const selectedImage = ref(null);
const isModalOpen = ref(false);
const selectedImageIndex = ref(null);

const handleImageClick = (index) => {
  selectedImageIndex.value = index;
  selectedImage.value = store.photoUrls[index];
  isModalOpen.value = true;
};

const closeModal = () => {
  isModalOpen.value = false;
  selectedImage.value = null;
  selectedImageIndex.value = null;
};

const nextImage = () => {
  if (selectedImageIndex.value !== null && selectedImageIndex.value < store.photoUrls.length - 1) {
    selectedImageIndex.value += 1;
    selectedImage.value = store.photoUrls[selectedImageIndex.value];
  }
};

const previousImage = () => {
  if (selectedImageIndex.value !== null && selectedImageIndex.value > 0) {
    selectedImageIndex.value -= 1;
    selectedImage.value = store.photoUrls[selectedImageIndex.value];
  }
};

const handleKeydown = (event) => {
  if (event.key === 'ArrowLeft') {
    previousImage();
  } else if (event.key === 'ArrowRight') {
    nextImage();
  }
};

const goToUploadPage = () => {
  router.push('/uploadImage'); // Navigate to the upload image page
};
</script>

<template>
  <div class="gallery-container">
    <!-- Gallery Header -->
    <header class="gallery-header">
      <h2 class="header-title">Image Gallery</h2>
      <p class="header-description">
        Click on an image to view it in full size and navigate through the gallery.
      </p>
    </header>

    <!-- If there are no images to display, show the upload button -->
    <div v-if="store.photoUrls.length === 0" class="no-images-container">
      <p>No images to display. Please upload some images.</p>
      <v-btn @click="goToUploadPage" color="primary" class="upload-button">
        Upload Images
      </v-btn>
    </div>

    <!-- Image Grid -->
    <div v-else class="gallery-grid">
      <v-row dense>
        <v-col
          v-for="(imgSrc, index) in store.photoUrls"
          :key="index"
          cols="12"
          sm="6"
          md="4"
          lg="3"
          xl="2">
          <v-img
            :src="imgSrc"
            aspect-ratio="1.67"
            class="gallery-image"
            @click="handleImageClick(index)">
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
    <v-dialog v-model="isModalOpen" max-width="80vw">
      <v-card class="modal-card">
        <v-img :src="selectedImage" class="enlarged-image" contain />
        <div class="modal-navigation">
          <v-btn icon @click="previousImage" :disabled="selectedImageIndex === 0">
            <v-icon>mdi-chevron-left</v-icon>
          </v-btn>
          <v-btn icon @click="nextImage" :disabled="selectedImageIndex === store.photoUrls.length - 1">
            <v-icon>mdi-chevron-right</v-icon>
          </v-btn>
        </div>
        <v-btn icon @click="closeModal" class="close-btn">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card>
    </v-dialog>
  </div>
</template>

<style scoped>
/* Styling for the header section */
.gallery-header {
  text-align: center;
  margin-bottom: 40px;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.header-title {
  font-size: 2rem;
  color: #333;
  font-weight: 600;
}

.header-description {
  font-size: 1.2rem;
  color: #666;
  margin-top: 10px;
}

.no-images-container {
  text-align: center;
  margin-top: 50px;
}

.no-images-container p {
  font-size: 16px;
  margin-bottom: 20px;
}

.upload-button {
  margin-top: 20px;
}

.gallery-grid {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
}

/* Modal & image styles */
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

.clickable-image {
  border: 1px dotted;
}
</style>
