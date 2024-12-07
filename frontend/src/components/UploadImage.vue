<script setup>
import axios from 'axios';
import { store } from '../store';
import { ref } from 'vue';
import {fetchAndStoreImages} from "@/controller/SynchronizeImages.js";

const successMessage = ref('');
const previewImages = ref([]);

const handleImageUpload = (event) => {
  const files = event.target.files;
  if (files && files.length > 0) {
    successMessage.value = '';
    for (const file of files) {
      const imageUrl = URL.createObjectURL(file);
      previewImages.value.push({ url: imageUrl, blob: file });
      store.photoUrls.push(imageUrl);
      store.photoBlobs.push(file);
    }
  }
};

const removePreviewImage = (index) => {
  previewImages.value.splice(index, 1);
};

const uploadImage = async () => {
  if (!previewImages.value.length) return;

  try {
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
      const { message, file_paths } = response.data;

      console.log('Images uploaded successfully:', message);
      console.log('Saved at:', file_paths);

      successMessage.value = 'Images uploaded successfully!';
      previewImages.value = [];

      fetchAndStoreImages();
    } else {
      console.error('Unexpected response:', response);
    }
  } catch (error) {
    console.error('Failed to upload images:', error);
  }
};
</script>

<template>
  <div class="upload-container">
    <!-- Success Message -->
    <div v-if="successMessage" class="success-message">
      <p>{{ successMessage }}</p>
    </div>

    <!-- Image Preview -->
    <div v-if="previewImages.length" class="image-preview-gallery">
      <h3>Preview Images:</h3>
      <div class="gallery">
        <div v-for="(item, index) in previewImages" :key="index" class="gallery-item">
          <img :src="item.url" alt="Preview Image" />
          <button class="remove-button" @click="removePreviewImage(index)">X</button>
        </div>
      </div>
    </div>

    <!-- File Upload and Buttons -->
    <div class="upload-actions">
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
        :disabled="!previewImages.length">
        Upload Images
      </button>
    </div>
  </div>
</template>

<style scoped>

.success-message {
  color: green;
  font-size: 18px;
  margin-bottom: 20px;
}

.upload-container {
  margin: 20px auto;
  text-align: center;
}

.upload-actions {
  margin: 20px;
}

.choose-image-button, .upload-image-button {
  margin: 5px;
  padding: 10px 20px;
  background-color: #007BFF;
  color: #fff;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
}

.choose-image-button:hover, .upload-image-button:hover {
  background-color: #0056b3;
}

.upload-image-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.gallery {
  display: flex;
  flex-wrap: nowrap;
  gap: 10px;
  overflow-x: auto;
}

.gallery-item {
  flex: 0 0 auto;
  position: relative;
}

.remove-button {
  position: absolute;
  top: 5px;
  right: 5px;
  background-color: red;
  color: white;
  border: none;
  border-radius: 3px;
  padding: 5px;
  cursor: pointer;
  font-size: 12px;
}

.remove-button:hover {
  background-color: darkred;
}

.gallery-item img {
  width: 100px;
  height: 100px;
  object-fit: cover;
  border: 1px solid #ccc;
  border-radius: 5px;
}
</style>