<script setup>
import { onMounted, ref } from 'vue';
import { store } from '../store'; // Assuming this is a reactive store
import { useRouter } from 'vue-router';
import { fetchAndStoreImages } from "@/controller/SynchronizeImages.js";

const router = useRouter();

const selectedImage = ref(null);
const isModalOpen = ref(false);
const selectedImageIndex = ref(null);

const handleImageClick = (index, type) => {
  selectedImageIndex.value = index;
  selectedImage.value = type === 'url' ? store.photoUrls[index] : getObjectUrl(store.galleryBlobs[index]);
  isModalOpen.value = true;
};

const getTotalImageCount = () => {
  return store.photoUrls.length + store.galleryBlobs.length;
};

const handleImageError = (index) => {
  console.error(`Image at index ${index} failed to load.`);
};

const closeModal = () => {
  isModalOpen.value = false;
  selectedImage.value = null;
  selectedImageIndex.value = null;
};

const nextImage = () => {
  if (selectedImageIndex.value !== null) {
    if (selectedImageIndex.value < store.photoUrls.length - 1 || selectedImageIndex.value < store.galleryBlobs.length - 1) {
      selectedImageIndex.value += 1;
      selectedImage.value = getSelectedImage();
    }
  }
};

const previousImage = () => {
  if (selectedImageIndex.value !== null && selectedImageIndex.value > 0) {
    selectedImageIndex.value -= 1;
    selectedImage.value = getSelectedImage();
  }
};

const getSelectedImage = () => {
  if (selectedImageIndex.value < store.photoUrls.length) {
    return store.photoUrls[selectedImageIndex.value];
  } else {
    const blobIndex = selectedImageIndex.value - store.photoUrls.length;
    return getObjectUrl(store.galleryBlobs[blobIndex]);
  }
};

const getObjectUrl = (blob) => {
  // If blob is a base64 string, return it directly as a data URL
  if (typeof blob === 'string' && blob.startsWith('data:')) {
    return blob; // It's already in data URL format
  }

  // Otherwise, convert it to a Blob URL (for actual Blob objects)
  const objectUrl = URL.createObjectURL(blob);
  return objectUrl;
};

// Ensure images are loaded on page load
onMounted(() => {
  fetchAndStoreImages(); // Optionally fetch additional images if needed
});

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
    <div v-if="store.photoUrls.length === 0 && store.galleryBlobs.length === 0" class="no-images-container">
      <p>No images to display. Please upload some images.</p>
      <v-btn @click="goToUploadPage" color="primary" class="upload-button">
        Upload Images
      </v-btn>
    </div>

    <!-- Section for photoUrls -->
    <div v-if="store.photoUrls.length > 0" class="gallery-section">
      <h3 class="section-title url-title">Photo URLs</h3>
      <div class="gallery-grid">
        <v-row dense>
          <v-col
              v-for="(imgSrc, index) in store.photoUrls"
              :key="'url-' + index"
              cols="6"
              sm="4"
              md="3"
              lg="2"
              xl="2">
            <v-img
                :src="imgSrc"
                aspect-ratio="1.8"
                class="gallery-image"
                @click="handleImageClick(index, 'url')"
                @error="handleImageError(index)">
              <template v-slot:placeholder>
                <v-row align="center" class="fill-height ma-0" justify="center">
                  <v-progress-circular color="grey-lighten-5" indeterminate></v-progress-circular>
                </v-row>
              </template>
              <template v-slot:error>
                <v-row align="center" justify="center" class="fill-height ma-0">
                  <v-icon color="red">mdi-alert-circle</v-icon>
                </v-row>
              </template>
            </v-img>
          </v-col>
        </v-row>
      </div>
    </div>

    <div v-if="store.galleryBlobs.length > 0" class="gallery-section">
      <h3 class="section-title url-title">Created Collages</h3>
      <div class="gallery-grid">
        <v-row dense>
          <v-col
              v-for="(blob, index) in store.galleryBlobs"
              :key="'blob-' + index"
              cols="6"
              sm="4"
              md="3"
              lg="2"
              xl="2">
            <v-img
                :src="getObjectUrl(blob)"
                aspect-ratio="1.3"
                class="gallery-image"
                @click="handleImageClick(index, 'blob')"
                @error="handleImageError(index)">
              <template v-slot:placeholder>
                <v-row align="center" class="fill-height ma-0" justify="center">
                  <v-progress-circular color="grey-lighten-5" indeterminate></v-progress-circular>
                </v-row>
              </template>
              <template v-slot:error>
                <v-row align="center" justify="center" class="fill-height ma-0">
                  <v-icon color="red">mdi-alert-circle</v-icon>
                </v-row>
              </template>
            </v-img>
          </v-col>
        </v-row>
      </div>
    </div>

    <!-- Modal for Enlarged Image -->
    <v-dialog v-model="isModalOpen" max-width="80vw">
      <v-card class="modal-card">
        <v-img :src="selectedImage" class="enlarged-image" contain/>
        <div class="modal-navigation">
          <v-btn icon @click="previousImage" :disabled="selectedImageIndex === 0">
            <v-icon>mdi-chevron-left</v-icon>
          </v-btn>
          <v-btn icon @click="nextImage" :disabled="selectedImageIndex === getTotalImageCount() - 1">
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

.section-title {
  font-size: 1.8rem; /* Larger font size */
  font-weight: 600; /* Bold font */
  text-align: center; /* Center alignment */
  padding: 10px; /* Add some padding */
  margin-bottom: 20px; /* Add space below the title */
  border-bottom: 2px solid #ddd; /* Decorative underline */
  color: #444; /* Darker text color */
}

/* URL Section Specific Title Styling */
.url-title {
  background-color: #e3f2fd; /* Light blue background */
  border-color: #90caf9; /* Light blue border */
  color: #1976d2; /* Dark blue text */
}

.gallery-section {
  margin: 30px 0;
}

.gallery-grid {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px; /* Adds spacing between images */
}

.gallery-image {
  border-radius: 8px; /* Slightly rounded corners */
  transition: transform 0.2s ease; /* Smooth scaling effect */
}

.gallery-image:hover {
  transform: scale(1.05); /* Scale up slightly on hover */
}
</style>
