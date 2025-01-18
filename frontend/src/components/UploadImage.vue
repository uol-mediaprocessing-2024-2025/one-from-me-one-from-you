<script setup>
import axios from 'axios';
import { store } from '../store';
import { ref } from 'vue';
import { fetchAndStoreImages } from "@/controller/SynchronizeImages.js";

const successMessage = ref('');
const previewImages = ref([]);
const messageStyle = ref({});

const handleImageUpload = (event) => {
  const files = event.target.files;
  if (files && files.length > 0) {
    successMessage.value = '';
    for (const file of files) {
      downscaleImage(file, 300, 300) // Downscale to max 300x300 (or any size you prefer)
        .then(({ url, blob }) => {
          previewImages.value.push({ url, blob });
        })
        .catch((error) => {
          console.error('Error downsizing image:', error);
        });
    }
  }
};

/**
 * Downscales an image to the specified width and height using a canvas.
 * @param {File} file - The original image file.
 * @param {number} maxWidth - The maximum width of the output image.
 * @param {number} maxHeight - The maximum height of the output image.
 * @returns {Promise<{url: string, blob: Blob}>} - A Promise that resolves with the downscaled image's URL and blob.
 */
const downscaleImage = (file, maxWidth, maxHeight) => {
  return new Promise((resolve, reject) => {
    const img = new Image();
    const reader = new FileReader();

    // Load the image file as a data URL
    reader.onload = (e) => {
      img.src = e.target.result;
    };

    reader.onerror = (err) => reject(err);

    // Once the image is loaded, resize it
    img.onload = () => {
      // Calculate the target dimensions while maintaining the aspect ratio
      const aspectRatio = img.width / img.height;
      let targetWidth = maxWidth;
      let targetHeight = maxHeight;

      if (aspectRatio > 1) {
        // Landscape
        targetHeight = maxWidth / aspectRatio;
      } else {
        // Portrait or square
        targetWidth = maxHeight * aspectRatio;
      }

      // Create a canvas to draw the resized image
      const canvas = document.createElement('canvas');
      canvas.width = targetWidth;
      canvas.height = targetHeight;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(img, 0, 0, targetWidth, targetHeight);

      // Convert the canvas back to a blob and create an object URL
      canvas.toBlob(
        (blob) => {
          if (blob) {
            const url = URL.createObjectURL(blob);
            resolve({ url, blob });
          } else {
            reject(new Error('Canvas conversion to Blob failed.'));
          }
        },
        file.type,
        0.8 // Quality factor (optional, between 0 and 1)
      );
    };

    img.onerror = (err) => reject(err);

    // Read the file as a data URL
    reader.readAsDataURL(file);
  });
};

const removePreviewImage = (index) => {
  previewImages.value.splice(index, 1);
};

const isUploading = ref(false); // Status variable for the upload
const statusMessage = ref(''); // Message for the user

const uploadImage = async () => {
  if (!previewImages.value.length) return;

  try {
    // Set status to "Uploading" and notify the user
    isUploading.value = true;
    statusMessage.value = 'Uploading images...';

    const formData = new FormData();

    previewImages.value.forEach((item, index) => {
      const fileExtension = item.blob.type.split('/')[1];
      const filename = `image_${index + 1}.${fileExtension}`;
      formData.append('files', item.blob, filename);
    });

    const response = await axios.post(`${store.apiUrl}/saveImages`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    if (response.status === 200) {
      successMessage.value = 'Images uploaded successfully!';
      statusMessage.value = ''; // Reset status message
      messageStyle.value = { backgroundColor: '#d4edda', color: '#155724', border: '1px solid #c3e6cb' }; // Green for success
      previewImages.value = [];
      await fetchAndStoreImages();
    } else {
      successMessage.value = 'An error occurred while uploading. Please try again.';
      statusMessage.value = ''; // Show error message and reset status
      messageStyle.value = { backgroundColor: '#f8d7da', color: '#721c24', border: '1px solid #f5c6cb' }; // Red for error
      console.error('Unexpected response:', response);
    }
  } catch (error) {
    successMessage.value = 'Failed to upload images. Please check your connection or try again later.';
    statusMessage.value = ''; // Show error message and reset status
    messageStyle.value = { backgroundColor: '#f8d7da', color: '#721c24', border: '1px solid #f5c6cb' }; // Red for error
    console.error('Failed to upload images:', error);
  } finally {
    isUploading.value = false; // Upload finished
  }
};
</script>

<template>
  <div class="upload-page">
    <!-- Page Header -->
    <header class="page-header">
      <h1 class="page-title">Upload Your Images</h1>
      <p class="page-description">
        Select images to preview them below. Remove any unwanted images before uploading them to the server.
      </p>
    </header>

    <!-- Feedback Messages -->
    <div v-if="successMessage" class="feedback-message" :style="messageStyle">
      <p>{{ successMessage }}</p>
    </div>

    <!-- Upload Actions -->
    <div class="upload-header">
      <button @click="() => $refs.fileInput.click()" class="choose-image-button">
        Choose Images
      </button>
      <input
        ref="fileInput"
        type="file"
        accept="image/*"
        @change="handleImageUpload"
        style="display: none;"
        multiple
      />
      <button
        @click="uploadImage"
        class="upload-image-button"
        :disabled="!previewImages.length || isUploading">
        {{ isUploading ? 'Uploading...' : 'Upload Images' }}
      </button>
    </div>

    <!-- Preview Gallery -->
    <div v-if="previewImages.length" class="preview-gallery">
      <h3 class="preview-title">Preview Selected Images</h3>
      <div class="gallery-grid">
        <div v-for="(item, index) in previewImages" :key="index" class="gallery-item">
          <img :src="item.url" alt="Preview Image" />
          <button class="remove-button" @click="removePreviewImage(index)">X</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* General Layout */
.upload-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  padding: 20px;
  width: 100%;
  height: 100vh;
  box-sizing: border-box;
  background: #f7f9fc;
}

/* Page Header */
.page-header {
  text-align: center;
  margin-bottom: 20px;
}

.page-title {
  font-size: 32px;
  font-weight: bold;
  color: #333;
}

.page-description {
  font-size: 18px;
  color: #555;
  margin-top: 10px;
}

.feedback-message {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 20px;
  padding: 10px;
  border-radius: 5px;
  text-align: center;
}

.feedback-message p {
  margin: 0;
}

.feedback-message {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.success-message {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

/* Upload Header */
.upload-header {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
}

.choose-image-button, .upload-image-button {
  padding: 12px 30px;
  font-size: 18px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: white;
}

.choose-image-button {
  background-color: #007bff;
}
.choose-image-button:hover {
  background-color: #0056b3;
}

.upload-image-button {
  background-color: #28a745;
}
.upload-image-button:hover {
  background-color: #218838;
}
.upload-image-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

/* Preview Gallery */
.preview-gallery {
  width: 100%;
  max-width: 1200px;
}

.preview-title {
  font-size: 24px;
  margin-bottom: 20px;
  text-align: center;
  color: #333;
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 20px;
  justify-items: center;
}

.gallery-item {
  position: relative;
  width: 150px;
  height: 150px;
  border: 1px solid #ccc;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.gallery-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-button {
  position: absolute;
  top: 8px;
  right: 8px;
  background-color: rgba(255, 0, 0, 0.8);
  color: white;
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.remove-button:hover {
  background-color: rgba(255, 0, 0, 1);
}
</style>
